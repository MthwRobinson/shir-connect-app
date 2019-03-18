# Shir Connect
[![coverage report](https://gitlab.com/fiddler-analytics/shir-connect/badges/master/coverage.svg)](https://gitlab.com/fiddler-analytics/shir-connect/commits/master)

## Getting Started

The following steps show how to get started with Shir Connect locally.
After completing these steps, you should be able to access Shir Connect at http://localhost

### Environment

To run Shir Connect locally, you'll need to add the following environmental variables `~/.bashrc`:
```
export APP_ENVIRONMENT="LOCAL"
export JWT_SECRET_KEY="{any_alphanumeric_sequence}"
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

After the setup steps are done, you can start the unit tests by running `py.test --cov=shir_connect` from the `/server` folder.

The Postgres database, which includes both schema and table definitions, can be initialized using the following CLI command:
```
shir_connect initialize
```

### UI

To install the UI, navigate to the `/ui` folder and run `npm install`.
After that, you can run `npm run start` to run a development server for the app.
To access the REST API, you will need to configure a web server to redirect `/` to `localhost:5000` and `/service` to `localhost:3000`.

### Running the Flask App

The REST API is a Flask app that can be launched from the CLI.
By default, the app runs on port 5000.
To start the REST API in development mode, run the following command:
```
shir_connect launch_api --debug
```
After that, the Flask app will be running on port 5000.
The Flask app using JSON web tokens (JWT) for authentication.
Before running the app, you'll need a user name and password.
Once you have a username and password, you can obtain a JWT using the following call: `curl -H "Content-Type: application/json" -X POST -d '{"username":"password"}' http://localhost:5000/service/user/authenticate`

### NGINX

In addition to installing launching the frontend and backend, you'll need an NGINX config such as the following to direct traffic on your local ports.

```
server {
  listen 80 default_server;
  listen [::]:80 default_server;

  location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
  }

  location /service {
    proxy_pass http://localhost:5000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
  }

}
```