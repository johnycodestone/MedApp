# Frontend foundation README

## Purpose
- Root-level template and static scaffolding for MedApp.
- Provides a consistent base layout (`base.html`), shared includes (`header.html`, `footer.html`, and reusable components), and design tokens.
- Bootstrap is included via CDN in `base.html`.
- Shared components live under `templates/includes/` and `static/css/components` / `static/js/components`.
- Each app is responsible for its own app‑specific templates and static assets, but should reuse root‑level components wherever possible.

## How to run
1. Ensure `settings.py` includes:
   - Templates dir: `os.path.join(BASE_DIR, 'templates')`
   - `STATICFILES_DIRS` includes `os.path.join(BASE_DIR, 'static')`
2. Run Django dev server:  
   ```bash
   python manage.py runserver
Open the staging page mapped by your URL or create a simple view that renders templates/pages/staging.html.

Shared components
The following reusable components are available at the root level:

Pagination

Template: templates/includes/pagination.html

CSS: static/css/components/pagination.css

JS: static/js/components/pagination.js

Breadcrumbs

Template: templates/includes/breadcrumbs.html

CSS: static/css/components/breadcrumbs.css

Filters (search + chips)

Template: templates/includes/filters.html

CSS: static/css/components/filters.css

JS: static/js/components/filters.js

CTA Bar (call-to-action strip)

Template: templates/includes/cta_bar.html

CSS: static/css/components/cta_bar.css

JS: static/js/components/cta_bar.js

How to include a shared component
In your app template, extend base.html and include the component:

django
{% extends "base.html" %}
{% block content %}
  {% include "includes/pagination.html" %}
{% endblock %}
In your app’s {% block styles %} and {% block scripts %}, load only the CSS/JS you need:

django
{% block styles %}
  <link rel="stylesheet" href="{% static 'css/components/pagination.css' %}">
{% endblock %}

{% block scripts %}
  <script src="{% static 'js/components/pagination.js' %}"></script>
{% endblock %}
This ensures each app only loads the assets it actually uses.

How to add a new shared component
Create template partial under templates/includes/<name>.html.

Add CSS under static/css/components/<name>.css.

Add JS under static/js/components/<name>.js if needed.

Document usage here in the README.

How to add an app-specific component
Create template under yourapp/templates/yourapp/<name>.html or partials/.

Add CSS under yourapp/static/yourapp/css/<name>.css.

Add JS under yourapp/static/yourapp/js/<name>.js.

Reference them in your app’s {% block styles %} and {% block scripts %}.

PR rules for foundation
This foundation was created by frontend lead(s).

Subsequent component PRs should not edit base.html, base.js, or base.css without approval.

Shared components should be added under templates/includes/ and static/components/ as described above.

App‑specific work must remain scoped to the app’s own templates/<app>/ and static/<app>/.