# TRS Analytics Dashboard

## Requirements

1. ETL pipeline to populate a database with data from the Eventbrite API (https://www.eventbrite.com/developer/v3/)
2. Visualization for TRS business metrics
3. Select users need access to the database
4. Users need to be able to export visualizations and upload them to Sharepoint
5. There needs to be an audit trail that tracks actions by users in the dashboard
6. Ability to export data in a `.csv` file on a monthly basis

## Installation

### Server 

To install the server side application navigate to the `/server` folder and run  `pip install -e .[test]`.
This will install dependencies for the app, as well as testing dependencies.

To connect to the Eventbrite API, you will need to obtain an OAUTH token. 
You can get one from the website linked above.
After you obtain your OAUTH key, run `export EVENTBRITE_OAUTH="{token}", replacing {token} with your OAUTH token.

To connect to Postgres, you need to add the user name and password to a `~/.pgpass` file.
The formate of the file is:
```
{host}:{port}:*:{user}:{password}
```

After the setup steps are done, you can start the unit tests by running `py.test --cov=trs\_dashboard` from the `/server` folder.

The Postgres database, which includes both schema and table definitions, can be initialized using the following CLI command:
```
trs_dashboard initialize
```

### UI

To install the UI, navigate to the `/ui` folder and run `npm install`.
After that, you can run `npm run start` to run a development server for the app.
To access the REST API, you will need to configure a web server to redirect `/` to `localhost:5000` and `/service` to `localhost:3000`.

## Operation

### Load Data

The process to load data from Eventbrite into Postgres can be launched from the CLI using the following command:
```
trs_dashboard load_eventbrite
```
This will load all of the Eventbrite data for events that start after the most recent dataload.
When new data is uploaded, it overwrites the current record.
Information for upcoming events will be updated until the event takes place.
All datetimes will be stored in the database as UTC.


