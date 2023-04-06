# Cloud Spanner GKE Sample

Sample application displaying Cloud Spanner and GKE integration.

This application is a simple registry of singers, which uses Cloud Spanner as a database. A screenshot of the application can be seen below:

![Singers Registry Screenshot](images/singers_registry.png)

## Running the application

### Locally

You can run the application directly from your machine by following the instructions below.

#### Before you start

To run the application locally you should have `nodejs` and `npm` installed.

You should configure your Cloud Spanner instance id and database id in the code. These can be configured through the following environment variables respectively: `CLOUD_SPANNER_INSTANCE` and `CLOUD_SPANNER_DATABASE`. Alternatively you can hardcode the values by modifying the [src/server.js](src/server.js) file.

You should have set up authentication and authorization for your Cloud Spanner instance and database. You can follow the [Cloud Spanner getting started guide](https://cloud.google.com/spanner/docs/getting-started/set-up) for more information.

#### Starting the server

```sh
# Builds the application and install dependencies
npm install && npm run build

npm start
```

You should see the web server available at port `8080` by default.

### Docker

You can also run the application using a Docker image.

#### Before you start

You will need to have your credentials exposed to the docker container, so that it can use Cloud Spanner. You can follow the [Cloud Spanner getting started guide](https://cloud.google.com/spanner/docs/getting-started/set-up) for more information.

#### Starting the server

Build the docker image.

```sh
docker build . -t sample-app
```

Run the docker image. Make sure to replace your GCP project id, Cloud Spanner instance and database name in the command below if you don't have the environment variables used set.

```sh
docker run \
    -v "$HOME/.config/gcloud:/gcp/config:ro" \
    --env GOOGLE_APPLICATION_CREDENTIALS=/gcp/config/application_default_credentials.json \
    --env GOOGLE_CLOUD_PROJECT_ID=$GOOGLE_CLOUD_PROJECT_ID \
    --env CLOUD_SPANNER_INSTANCE=$CLOUD_SPANNER_INSTANCE \
    --env CLOUD_SPANNER_DATABASE=$CLOUD_SPANNER_DATABASE \
    -p 8080:8080 \
    sample-app
```

You should see the web server available at port `8080` by default.