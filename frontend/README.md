Frontend foundation README

Purpose
- Root-level template and static scaffolding for MedApp.
- Bootstrap is included via CDN in base.html.
- Other devs add component templates under templates/components and static files under static/css/components and static/js/components.

How to run
1. Ensure settings.py includes:
   - templates dir: os.path.join(BASE_DIR, 'templates')
   - STATICFILES_DIRS includes os.path.join(BASE_DIR, 'static')
2. Run Django dev server: python manage.py runserver
3. Open the staging page mapped by your URL or create a simple view that renders templates/pages/staging.html

How to add a component
1. Create template: templates/components/<name>/index.html
2. Create JS: static/js/components/<name>.js
   - In JS call MedApp.register('Name', { init: function(el, props){ ... } })
3. Add CSS: static/css/components/<name>.css and reference it either on the page using {% block styles %} or let component JS inject it when needed.

PR rules for foundation
- This foundation was created by frontend lead(s). Subsequent component PRs should not edit base.html, base.js or base.css without approval.
