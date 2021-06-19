# Project setup guidelines

## Run Project With Docker.

1. `docker-compose build server` First build server service.
2. `docker-compose run --rm server python manage.py createsuperuser` Create Superuser if needed.
3. `docker-compose run --rm server python manage.py populate_data` Create 100 products with related categories and stock if needed.
4. `docker-compose up server` Run Project with this command and (visit here)[http://localhost:8000].


## Setup Project with venv.

1. Install venv from (here)[https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/]
2. Navigate to the project directory and activate venv.
3. `cd server/` navigate to manage.py file.
4. `pip install -r requirements.txt` Install required package.
5. `manage.py createsuperuser` Create Superuser if needed.
6. `python manage.py populate_data` Create 100 products with related categories and stock if needed.
7. `python manage.py runserver` Run Project with this command and (visit here)[http://localhost:8000].
