

-----

````markdown
# Prompt for GitHub Copilot: Initial Django Project Setup for IoT Dashboard

**Goal:** Create the complete directory structure and virtual environment for a new Django project. This project will serve as the backend and frontend for an IoT dashboard.

The final structure should be clean, follow best practices, and be ready for developing the first app.

---

### Step 1: Create Project Directory and Virtual Environment

This step ensures our project has its own isolated space and dependencies.

1.  Create a new directory for the project named `django_iot_dashboard`.
2.  Navigate into the new directory.
3.  Create a Python virtual environment inside this directory. A standard name for it is `venv`.
4.  Activate the virtual environment. Provide the correct command for both Windows and macOS/Linux.

**Provide the shell commands for these actions:**

```bash
# 1. Create and enter the directory
mkdir django_iot_dashboard
cd django_iot_dashboard

# 2. Create the virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
# .\venv\Scripts\activate
#
# On macOS/Linux:
# source venv/bin/activate
````

-----

### Step 2: Install Django and Create Project Structure

With the environment active, we will install Django and create the project files.

1.  Install the latest version of Django using `pip`.
2.  Create a `requirements.txt` file to keep track of our project's dependencies. This is a crucial best practice.
3.  Create a new Django project named `dashboard_project`. **Important:** Create it in the current directory to avoid unnecessary folder nesting.
4.  Create the first Django app, which will handle all our dashboard logic, and name it `iot_dashboard`.

**Provide the shell commands for these actions:**

```bash
# 1. Install Django
pip install django

# 2. Save the dependency
pip freeze > requirements.txt

# 3. Create the Django project in the current directory (note the dot at the end)
django-admin startproject dashboard_project .

# 4. Create our first app
python manage.py startapp iot_dashboard
```

-----

### Step 3: Initial Configuration and Verification

Finally, let's configure the project to recognize our new app and verify that everything is working.

1.  Open the main settings file (`dashboard_project/settings.py`).
2.  Add our new `'iot_dashboard'` app to the `INSTALLED_APPS` list.
3.  Run the initial database migrations to set up Django's default tables.
4.  Start the development server to confirm the project runs without errors.

**Provide the configuration change and shell commands:**

```python
# In dashboard_project/settings.py, modify INSTALLED_APPS:

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'iot_dashboard',  # <<< Add this line
]
```

```bash
# 3. Run initial database migrations
python manage.py migrate

# 4. Start the development server
python manage.py runserver
```

After running the server, I should be able to open `http://127.0.0.1:8000` in my web browser and see the default Django welcome page.

```
```