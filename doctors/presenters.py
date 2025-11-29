# doctors/presenters.py
"""
Presenters module (Factory + Adapter)
- Responsibility: convert model instances or raw values into template-ready dicts.
- Purpose: AUTOMATE mapping so templates only render and users never map fields manually.
- SOLID:
  - SRP: each function has a single job (adapt a model or build an action dict).
  - DIP: views depend on these functions rather than model internals.
- Patterns:
  - Factory: build_action centralizes creation of quick-action dicts and resolves URLs.
  - Adapter: appointment_adapter, shift_adapter, patient_adapter, report_adapter normalize model shapes.
- Safety: uses getattr and try/except to tolerate model changes and missing fields.
"""

from django.urls import reverse, NoReverseMatch
from django.utils import timezone

def _try_resolve_url(candidates, arg=None):
    """
    Try to reverse a list of candidate url names. Return first successful href or None.
    candidates: iterable of url name strings (may include namespace).
    arg: optional single positional arg to pass to reverse.
    """
    for name in candidates:
        try:
            return reverse(name, args=[arg]) if arg is not None else reverse(name)
        except NoReverseMatch:
            continue
    return None


def build_action(label, icon=None, url_name=None, url_arg=None, variant=None, aria_label=None, href=None):
    """
    Build a robust quick action dict for templates.
    - Resolve url_name to href here (templates won't call {% url %}).
    - If reverse fails, href will be None and templates render a disabled button.
    """
    if href is None and url_name:
        try:
            href = reverse(url_name, args=[url_arg]) if url_arg is not None else reverse(url_name)
        except NoReverseMatch:
            href = None
    return {
        "label": label,
        "icon": icon,
        "variant": variant,
        "aria_label": aria_label or label,
        "href": href,
        "url_name": None,
        "url_arg": None,
    }


def appointment_adapter(appt):
    """
    Convert an Appointment instance (appointments.models.Appointment) into the mini_card shape.
    Expected keys: title, subtitle, image_url, badges, kpis, href, aria_label
    URL resolution candidates include the names present in appointments/urls.py.
    """
    # Patient name extraction (defensive)
    patient_name = None
    try:
        patient = getattr(appt, "patient", None)
        if patient is not None:
            patient_name = (patient.get_full_name() if hasattr(patient, "get_full_name") else getattr(patient, "username", str(patient)))
    except Exception:
        patient_name = None

    scheduled = getattr(appt, "scheduled_time", None)
    title = patient_name or getattr(appt, "title", None) or str(appt)

    # Subtitle: formatted scheduled time or reason
    subtitle = ""
    if scheduled:
        try:
            subtitle = timezone.localtime(scheduled).strftime("%b %d, %Y %I:%M %p")
        except Exception:
            subtitle = str(scheduled)
    else:
        subtitle = getattr(appt, "reason", "") or ""

    status = getattr(appt, "status", None)
    badges = [{"label": str(status), "variant": "warning"}] if status else []

    kpis = []
    if scheduled:
        kpis.append({"label": "When", "value": subtitle})

    # Resolve appointment detail URL using known candidates from appointments/urls.py
    href = _try_resolve_url(
        [
            "appointments:appointment-detail",  # matches appointments/urls.py
            "appointments:detail",
            "appointments:appointment-api-detail",
            "appointments:appointment_detail",
        ],
        arg=getattr(appt, "id", None)
    )

    return {
        "title": title,
        "subtitle": subtitle,
        "image_url": None,
        "badges": badges,
        "kpis": kpis,
        "href": href,
        "aria_label": f"Appointment with {title}",
    }


def shift_adapter(shift):
    """
    Convert a Shift (schedules.models.Shift) or shift-like object into mini_card shape.
    Uses schedules app naming and fields where available.
    """
    title = getattr(shift, "title", None) or f"Shift {getattr(shift, 'id', '')}"
    # Prefer start_time for subtitle if present
    when = getattr(shift, "start_time", None) or getattr(shift, "when", None)
    subtitle = str(when) if when else ""
    # Active state detection
    state = getattr(shift, "is_active", None)
    badges = [{"label": "Active" if state else "Inactive", "variant": "info"}] if state is not None else []
    kpis = []
    try:
        duration_fn = getattr(shift, "duration_minutes", None)
        if callable(duration_fn):
            mins = duration_fn()
            kpis.append({"label": "Duration", "value": f"{mins}m"})
    except Exception:
        pass

    # Try to resolve schedule dashboard or calendar if useful (no per-shift detail assumed)
    href = _try_resolve_url(["schedules:schedule-dashboard", "schedules:schedule-calendar", "schedules:schedule-list"])

    return {
        "title": title,
        "subtitle": subtitle,
        "image_url": None,
        "badges": badges,
        "kpis": kpis,
        "href": href,
        "aria_label": f"Shift {title}",
    }


def patient_adapter(patient):
    """
    Convert a PatientProfile or user-like object into mini_card shape.
    """
    title = None
    try:
        if hasattr(patient, "full_name"):
            title = getattr(patient, "full_name")
        elif hasattr(patient, "user") and hasattr(patient.user, "get_full_name"):
            title = patient.user.get_full_name()
        elif hasattr(patient, "get_full_name"):
            title = patient.get_full_name()
        else:
            title = str(patient)
    except Exception:
        title = str(patient)

    subtitle = getattr(patient, "last_visit", "") or ""
    image_url = getattr(patient, "avatar_url", None) or None

    # Try to resolve patient profile URL using patients app names
    href = _try_resolve_url(["patients:profile", "patients:detail", "patients:profile-page"], arg=getattr(getattr(patient, "user", None), "id", None))

    return {
        "title": title,
        "subtitle": subtitle,
        "image_url": image_url,
        "badges": [],
        "kpis": [],
        "href": href,
        "aria_label": f"Patient {title}",
    }


def report_adapter(report):
    """
    Convert a report-like object into mini_card shape.
    """
    title = getattr(report, "title", None) or str(report)
    subtitle = getattr(report, "summary", "") or ""
    href = _try_resolve_url(["reports:dashboard", "reports:detail", "reports:report-detail"], arg=getattr(report, "id", None))
    return {
        "title": title,
        "subtitle": subtitle,
        "image_url": None,
        "badges": [],
        "kpis": [],
        "href": href,
        "aria_label": f"Report {title}",
    }
