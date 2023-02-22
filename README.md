# Yatube

Description: Simple project for posting, commenting some different stuff

Used technologies:
-
    - Python 3.7.9
    - Django 2.2.16
    - Django ORM
    - Sqlite3
    - Django Rest Framework 3.12.4
    - Simple JWT 4.7.2
    - Pytest 4.4.0
    - django-simple-captcha 0.5.17
    - python-dotenv==0.21.1

Features:
-
    - You can make posts with images in different groups
    - You can add comment posts and other's comments
    - You can edit and delete your posts
    - Added authentication/registration
    - Added feedback
    - Added API support
    - Added support for sending emails

## Installation:
- Clone the repository
- Create, activate virtual env and install requirements: 
##### pip install -r requirements.txt
- make migrations, migrate and launch the server
##### python manage.py makemigrations
##### python manage.py migrate
##### python manage.py runserver

After that site is available at your localhost url 
(most common case: http://127.0.0.1:8000/)


Author: Larkin Michael