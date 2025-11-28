# Schedules Frontend - Setup & Troubleshooting Guide

## Quick Start

1. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Access the pages:**
   - Doctor Schedules: http://127.0.0.1:8000/schedules/doctor/
   - Hospital Schedules: http://127.0.0.1:8000/schedules/hospital/

## Common Issues & Solutions

### 1. Page Not Loading / 404 Error
- **Check URL**: Make sure you're using the correct URLs:
  - `/schedules/doctor/` (with trailing slash)
  - `/schedules/hospital/` (with trailing slash)
- **Check server**: Ensure Django server is running on port 8000

### 2. Template Not Found Error
- Templates are located at:
  - `schedules/templates/schedules/doctor_schedules.html`
  - `schedules/templates/schedules/hospital_schedules.html`
- Django should auto-discover these with `APP_DIRS = True` in settings

### 3. Static Files Not Loading (CSS/JS missing)
- **Solution 1**: Run collectstatic:
  ```bash
  python manage.py collectstatic --noinput
  ```
- **Solution 2**: In development, Django should serve static files automatically if `DEBUG = True`
- **Check**: Static files are at:
  - `schedules/static/schedules/css/doctor_schedules.css`
  - `schedules/static/schedules/css/hospital_schedules.css`
  - `schedules/static/schedules/js/doctor_schedules.js`
  - `schedules/static/schedules/js/hospital_schedules.js`

### 4. Login Required Error
- Both pages require authentication (`@login_required`)
- **Doctor Schedules**: User must have role `DOCTOR` and a doctor profile
- **Hospital Schedules**: User must have role `HOSPITAL` and a hospital profile
- If not logged in, you'll be redirected to login page

### 5. Empty Page / No Data
- This is normal if there's no data in the database
- The pages will show "empty state" messages
- To test with data:
  - Create doctor/hospital profiles via Django admin
  - Add duties, shifts, schedules via admin or API

### 6. Python Errors
- Check the Django console/terminal for error messages
- Common issues:
  - Missing imports (should be fixed)
  - Database errors (run migrations if needed)
  - Model field errors

## Testing Steps

1. **Verify server is running:**
   ```bash
   python manage.py runserver
   ```
   You should see: "Starting development server at http://127.0.0.1:8000/"

2. **Test URL routing:**
   - Visit: http://127.0.0.1:8000/schedules/
   - Should show the schedule dashboard

3. **Test doctor schedules:**
   - Login as a doctor user
   - Visit: http://127.0.0.1:8000/schedules/doctor/
   - Should show doctor schedules page (even if empty)

4. **Test hospital schedules:**
   - Login as a hospital user
   - Visit: http://127.0.0.1:8000/schedules/hospital/
   - Should show hospital schedules page (even if empty)

## File Structure Verification

```
schedules/
├── templates/
│   └── schedules/
│       ├── doctor_schedules.html
│       └── hospital_schedules.html
├── static/
│   └── schedules/
│       ├── css/
│       │   ├── doctor_schedules.css
│       │   └── hospital_schedules.css
│       └── js/
│           ├── doctor_schedules.js
│           └── hospital_schedules.js
├── views.py (contains doctor_schedules_view and hospital_schedules_view)
└── urls.py (contains routes for /doctor/ and /hospital/)
```

## Debugging

If pages still don't load:

1. **Check browser console** (F12) for JavaScript errors
2. **Check Django terminal** for Python errors
3. **Check network tab** (F12) to see if static files are loading
4. **Verify user is logged in** and has correct role
5. **Check Django admin** to verify models exist

## Need Help?

If you see a specific error message, share:
- The exact error text
- What URL you're trying to access
- Whether you're logged in and as what role
- Any console/terminal error messages

