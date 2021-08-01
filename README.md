# Remedica Backend
Backend for an online pharmacy specialized on chronic patients. This was part of the Managing Product Development (MPD) Course at the Center for Digital Technology Management in Spring 2021.
<br>
This was hosted on Heroku and was mainly used by a Flutter-based [frontend application](https://github.com/manoletre99/mpd_frontend).

## Setup
** Branch `master` is the main branch.**
The backend can either be directly connected to a running Heroku instance (all necessary configuration files are already included in the repository) or run locally. For the former after setting up the required Heroku instances for the REST APIs and for the PostgresDB, the GitHub Repo can be connected and then the migrations have to be created once in order to set up the database. Before the final deployment to production the CORS settings have to be changed to only allow the hosted backend IP as allowed host (change `ALLOWED_HOSTS=[*]` in “medicaite/settings.py”). To run the backend locally one has to change the settings to `DEBUG=True` in “medicaite/settings.py”, create a local postgresDB instance and then start the django app as usual with “python manage.py runserver”. The postgresDB has to have the name and access credentials specified in “medicaite/settings.py”. Data can be added to the database using the standard admin panel of any django app, accessible at `localhost:8000/admin`. For the specific REST API endpoints see the technical description in section five. \\
**Important Notes:** 
* three session variables need to be defined before running the code: `SECRET_KEY` with the django project secret key, `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` for the access to the patient mail server. (use `export SECRET_KEY="..."` in terminal to define the variables, in Heroku they can be configured under Config Values). 
* running the project as is expects you to have a PostgresDB up and running called `medicaite_database` with user `medicaite_admin` and password `medicaite21`. To change that go to `/medicaite/settings.py` and change the respective database settings. 

## Endpoints
All APIs are created with help of the Django REST API framework plug-in for Django. This also includes an automatic “browseable API interface” that allows to easily test the APIs manually with specific input. This means when accessing the given URLs below a standard UI enables to easily send specific requests to the backend. For the currently deployed online version we provide specific test input (based on the current test data) to test the backend API. Once accessing the URLs one can also see what output data the backend returns in what specific format. In case an “not found” message comes back this means the database was changed - this can be however easily reconfigured by adding some toy data through the admin panel.

* In all APIs where medications are returned, the standard format for medications is the following (very important for backend-frontend-communication).
```
{
    "medication_name": "Injection2",
    "medication_id": 4,
    "medicationType": "Injection",
    "time": "twice a day",
    "totalPriceInEur": 100.0,
    "boughtTime": "15-Jun-2021 (09:51:02.000000)",
    "dosageInMg": 5,
    "totalDosage": 50,
    "daysLeft": 50,
    "totalDays": 50,
    "prescription": true,
    "description": "",
    "status": "accepted",
    "prescription_id": 3
}

```

* Redeem Medication API
  * /quickstart/api/redeem_prescription/
  * Example input: `{"ids":[{"medication_id":1,"patient_id":1}]}`
 
* Current Medication API
  * /quickstart/api/current_medication/
  * Example input: `{"patient_id":1}`
  * Sorted by daysLeft in ascending order

* New Prescription API
  * /quickstart/api/new_prescriptions/
  * Example input: `{"patient_id":1}`
  * Sorted by daysLeft in ascending order
  
* Reorder Prescription API
  * /quickstart/api/reorder_prescription/
  * Example input:
  * ```
    {
    "doctor_id":1,
    "email_body":"Hi Dr. Gergana, I would like to renew the prescription for the Ibu.Thanks and have a nice day, Maria",
    "prescription_id":33
    }
    ```

* Doctor Response API
  * /quickstart/api/answer_request/30/accepted
   * this specific link updates the status of prescription_id=30 to 'accepted'
  
* Responsible Doctors API
  * /quickstart/api/responsible_doctors/
  * Example input: `{"patient_id":1, "medication_ids":[1, 3, 7]}`

--> All example input is based on our version of the database. Add elements to your database with the django admin panel and adapt the input accordingly.

Other all inc. tools we considered but didn't use: 
* [ONLINE Shop Django Tool](https://django-shop.readthedocs.io/en/latest/architecture.html)
