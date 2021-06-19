# Project setup guidelines

- `git clone git@github.com:nayan32biswas/django-crud.git` Clone the project and navigate the folder by command line.

## Run Project With Docker.

1. `docker-compose build server` First build server service.
2. `docker-compose run --rm server python manage.py migrate` Initialize DB/Create DB.
3. `docker-compose run --rm server python manage.py createsuperuser` Create Superuser if needed.
4. `docker-compose run --rm server python manage.py populate_data` Create 100 products with related categories and stock if needed.
5. `docker-compose run --rm server python manage.py collectstatic` Load static files.
6. `docker-compose up server` Run Project with this command and [visit here](http://localhost:8000).


## Setup Project with venv.

1. Install venv from [here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).
2. Navigate to the project directory and activate venv.
3. `cd server/` navigate to server directory where the manage.py file located.
4. `pip install -r requirements.txt` Install required package.
5. `python manage.py migrate`  Initialize DB/Create DB.
6. `manage.py createsuperuser` Create Superuser if needed.
7. `python manage.py populate_data` Create 100 products with related categories and stock if needed.
8. `python manage.py collectstatic` Load static files.
9. `python manage.py runserver` Run Project with this command and [visit here](http://localhost:8000).
