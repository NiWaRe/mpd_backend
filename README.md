# Remedica Backend
Backend for an online pharmacy specialized on chronic patients. This was part of the Managing Product Development (MPD) Course at the Center for Digital Technology Management in Spring 2021.
<br>
This was hosted on Heroku and was mainly used by a Flutter-based [frontend application](https://github.com/manoletre99/mpd_frontend).

## Setup
The backend can either be directly connected to a running Heroku instance (all necessary configuration files are already included in the repository) or run locally. For the former after setting up the required Heroku instances for the REST APIs and for the PostgresDB, the GitHub Repo can be connected and then the migrations have to be created once in order to set up the database. Before the final deployment to production the CORS settings have to be changed to only allow the hosted backend IP as allowed host (change `ALLOWED_HOSTS=[*]` in “medicaite/settings.py”). To run the backend locally one has to change the settings to `DEBUG=True` in “medicaite/settings.py”, create a local postgresDB instance and then start the django app as usual with “python manage.py runserver”. The postgresDB has to have the name and access credentials specified in “medicaite/settings.py”. Data can be added to the database using the standard admin panel of any django app, accessible at `localhost:8000/admin`. For the specific REST API endpoints see the technical description in section five. \\
**Important Note:** three session variables need to be defined before running the code: `SECRET_KEY` with the django project secret key, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` for the access to the patient mail server. (use `export SECRET_KEY="..."` in terminal to define the variables, in Heroku they can be configured under Config Values). 

Other all inc. tools we considered but didn't use: 
* [ONLINE Shop Django Tool](https://django-shop.readthedocs.io/en/latest/architecture.html)
