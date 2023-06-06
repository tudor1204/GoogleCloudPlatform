# Steps to deploy v2 GKE container recommendations
This script and terraform:
- Creates an Artifact repo and stores the image necessary for Cloud Run
- Deploys a Cloud Run Job which export GKE metrics from Cloud Monitor
- Creates a Cloud Scheduler
- Creates a BigQuery table `gke_metrics` and two BigQuery views `container_recommendations` & `workloads-at-risk`

# Recommendations
- Default window period 2 weeks
- Memory recommendation: Max Memory Usage  during the window period + 25% buffer for memory requests and limits. The output is in mebiBytes. 
- CPU recommendation: Sets desired CPU utlization target of 70% based on the CPU usage during the window period and adds a buffer of 20%.

1. Set environment variables
    `export PROJECT_ID=[PROJECT_ID]
    gcloud config set project $PROJECT_ID


    export REGION=us-central1

    export BIGQUERY_DATASET=data
    export BIGQUERY_TABLE=gke_metrics
    export IMAGE=$REGION-docker.pkg.dev/$PROJECT_ID/docker-repo/vpa-recs-image:v2`

1. Clone the repo or pull new updates and navigate to v2 folder

    `git clone https://github.com/aburhan/kubernetes-engine-samples.git && cd kubernetes-engine-samples/gke-vpa-recommendations/v2`

1. Enable services

    `gcloud services enable cloudresourcemanager.googleapis.com \
        bigquery.googleapis.com run.googleapis.com \
        cloudbuild.googleapis.com \
        cloudscheduler.googleapis.com \
        artifactregistry.googleapis.com \
        iam.googleapis.com`

1. Create repo and push code to artifact repo
    `gcloud artifacts repositories create docker-repo --repository-format=docker \
    --location=$REGION --description="Docker repository"`


    `gcloud auth configure-docker \
        $REGION-docker.pkg.dev`


    `gcloud builds submit --tag $IMAGE`


1. Deploy Terraform
    `terraform -chdir=terraform init`
    `terraform -chdir=terraform apply -var project_id=$PROJECT_ID -var region=$REGION -var image=$IMAGE`


1. Run Cloud Scheduler to trigger Cloud Run job
    `gcloud scheduler jobs run recommendation-schedule --location=$REGION`

* Note Wait for Cloud Run job to complete *
1. Navigate to BigQuery and view results in BigQuery
`"SELECT * FROM ${PROJECT_ID}.data.container_recommendations"`
