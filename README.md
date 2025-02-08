# About the project

A LMS (Learning Management System) website, that offer courses and some benefits base on subscription plan.
This a SaaS (Software as a Service) website, that offers great user expersience and interface

# Tech stack
   - Stripe(payment gateway)
   - Django (Fullstack)
   - Neon PostgreSQL(Database for storing user data)
   - AWS3 (Database for storing user files)
   - Tailwind CSS(frontend styling)
   - Docker (For packaging to deployment)

# Getting Started
- Start your environment 
```
python -m venn venv
```
- Activate virtual environment
```
venv/Scripts/activate
```
- install dependecies
```
pip install -r requirements.txt
```
- Navigate to src folder
```
cd src
```
- Create a .env file, there is a .env.example for your perusal
- Start the server
```
python manage.py vendor_pull
python manage.py collectstatic
python manage.py runsever
```
