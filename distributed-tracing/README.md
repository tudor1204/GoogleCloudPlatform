# Pre-requisites

1.  GCP project
2.  `gcloud` and `skaffold` installed

# Steps

1.  Set up environment

    ```
    export PROJECT_ID=<project-id>
    export LOCATION=us-west1
    gcloud config set project $PROJECT_ID
    gcloud auth login
    gcloud auth application-default login
    gcloud auth configure-docker $LOCATION-docker.pkg.dev
    ```

1.  Create GKE cluster

    ```
    gcloud container clusters create-auto demo-cluster \
        --zone=$LOCATION
    ```

1.  Create SA and add role
    ```
    gcloud iam service-accounts create trace-demo
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member "serviceAccount:trace-demo@$PROJECT_ID.iam.gserviceaccount.com" \
        --role roles/cloudtrace.agent
    gcloud iam service-accounts add-iam-policy-binding trace-demo@$PROJECT_ID.iam.gserviceaccount.com \
        --role roles/iam.workloadIdentityUser \
        --member "serviceAccount:$PROJECT_ID.svc.id.goog[default/trace-demo]"
    kubectl create serviceaccount trace-demo
    kubectl annotate serviceaccount trace-demo \
        --namespace default \
        iam.gke.io/gcp-service-account=trace-demo@$PROJECT_ID.iam.gserviceaccount.com    ```

1.  Create Artifact Repository

    ```
    gcloud artifacts repositories create distributed-tracing \
        --repository-format=docker \
        --location $LOCATION
    ```

1.  Set default repo for Skaffold

    ```
    skaffold config set default-repo \
        $LOCATION-docker.pkg.dev/$PROJECT_ID/distributed-tracing
    ```

1.  Run

    ```
    skaffold dev --port-forward
    ```

1.  Test