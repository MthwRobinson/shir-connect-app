# TRS Analytics Dashboard

## Requirements

1. ETL pipeline to populate a database with data from the Eventbrite API (https://www.eventbrite.com/developer/v3/)
2. Visualization for TRS business metrics
3. Select users need access to the database
4. Users need to be able to export visualizations and upload them to Sharepoint
5. There needs to be an audit trail that tracks actions by users in the dashboard
6. Ability to export data in a `.csv` file on a monthly basis

## Installation

### Dependencies

The TRS Dashboard app dependings on a number of Debian dependencies. The dependencies include Postgres, Python virtual environments and node. These can be install by running `sudo sh scripts/install_dependencies.sh`

In addition, the following environmental variables need to be added to `~/.bashrc`:
```
export APP_ENVIRONMENT="LOCAL"
export EVENTBRITE_OAUTH="{eventbrite_token}"
export JWT_SECRET_KEY="{any_alphanumeric_sequence"
```

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

### Running the app persistently

The production app runs persistently using `pm2`. To start the application, you can run:
```
pm2 start scripts/start_app.sh
```

After the app is started, `pm2 stop <id>` will stop the app, `pm2 start <id>` will start the app and the `pm2 restart <id>` will restart the app. You can determin the id by running `pm2 list`.

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

The data load can also be run using `sh scripts/load_eventbrite.sh`. To schedule a daily load, run `crontab -e` and add the following line:
```
30 1 * * * /bin/sh /home/ubuntu/trs-dashboard/script/load_eventbrite.sh
```

### Running the Flask App

The REST API is a Flask app that can be launched from the CLI.
By default, the app runs on port 5000.
To start the REST API in development mode, run the following command:
```
trs_dashboard launch_api --debug
```
After that, the Flask app will be running on port 5000.
The Flask app using JSON web tokens (JWT) for authentication.
Before running the app, you'll need a user name and password.
Once you have a username and password, you can obtain a JWT using the following call: `curl -H "Content-Type: application/json" -X POST -d '{"username":"password"}' http://localhost:5000/service/user/authenticate`

After that you should be able to run `curl -H "Authorization: Bearer {JWT}" http://localhost:5000/service/test1` replacing `{JWT}` with your web token.
That will return the following output.
```
{
  "status": "success",
  "message": "Hello, friend!"
}
```

The production Flask app runs a WSGI server using gunicorn.
You can start the production app using the following command.
```
trs_dashboard launch_api --prod
```
Note that the WSGI server will run in the context of the terminal session where it is launched.
For production, the Flask app should be launched using `init.d`, `systemctl` or similar.
