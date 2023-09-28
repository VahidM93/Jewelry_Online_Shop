# Jewelry_Online_Shop
Welcome to the Django Online Shop project!

About project
This is my first comprehensive django project. This Django-based web application provides a seamless online shopping experience. It aims to be a feature-rich, user-friendly, and secure e-commerce platform. If you have any questions, suggestions, or issues regarding the project, please feel free to reach out to me.

vahid9068@gmail.com


Technologies Used
Django: The web framework used for building the online shop project.
PostgreSQL: The database management system used for storing data.
Redis: Used for caching and as the Celery message broker.
Celery: Used for task management, such as sending emails to customers asynchronously.
Docker: Used for containerization and deployment of the project.
Gunicorn: A Python WSGI HTTP server used for serving the Django application.
Nginx: A web server used as a reverse proxy and for serving static files.
HTML5, CSS, and JavaScript: The trio of technologies employed for front-end development, providing structure, styling, and interactivity to the web pages.
Yasg: Swagger library used for API documentation.
Initialization
To get started with the project, follow these steps:

Create a virtual environment and activate it:

On Windows:
python -m venv venv
.\venv\Scripts\activate.bat
On Linux:
python -m venv venv
source venv/bin/activate
Install the project requirements:

pip install -r requirements.txt
Running the Project
To run the project locally, perform the following commands:

Start Redis for caching and as the Celery message broker:

sudo service redis-server start
Start the Celery worker:

On Windows:
celery -A OnlineShop worker -l info -P solo
On Linux:
celery -A OnlineShop worker -l info
Apply database migrations:

python manage.py makemigrations
python manage.py migrate
Run the development server:

python manage.py runserver
Test Coverage
To run the unit tests and obtain the test coverage report, use the following command:

coverage run --source='.' manage.py test .
coverage report
The coverage report will provide information about the test coverage achieved by the project which covers more than 90% of the codebase.

Deployment
The project can be deployed using Docker, Gunicorn, and Nginx. To deploy the project, use the following command:

docker-compose up --build
API Documentation
API documentation for the project is available through Swagger.

Contributing
We welcome contributions from the community to improve the project. If you would like to contribute, please follow these steps:

Fork the repository and clone it to your local machine.
Create a new branch for your feature or bug fix.
Make the necessary changes and commit them.
Push your changes to your forked repository.
Submit a pull request describing the changes you've made.
