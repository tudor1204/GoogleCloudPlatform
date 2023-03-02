
echo "Create a service account to run the pipeline"
gcloud iam service-accounts create mql-export-metrics \
--display-name "MQL export metrics SA" \
--description "Used for the function that export monitoring metrics"

echo "Assigning IAM roles to the service account..."
gcloud projects add-iam-policy-binding  $PROJECT_ID --member="serviceAccount:mql-export-metrics@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/monitoring.viewer"
gcloud projects add-iam-policy-binding  $PROJECT_ID --member="serviceAccount:mql-export-metrics@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding  $PROJECT_ID --member="serviceAccount:mql-export-metrics@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/bigquery.dataOwner"
gcloud projects add-iam-policy-binding  $PROJECT_ID --member="serviceAccount:mql-export-metrics@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/bigquery.jobUser"

echo "Creating the Pub/Sub topic..."
gcloud pubsub topics create metric_export


#1. Run the following command to create a new Docker repository 
gcloud artifacts repositories create main --repository-format=docker \
--location=$REGION --description="Metrics exporter repository"

#2. Configure access to the repository
gcloud auth configure-docker $REGION-docker.pkg.dev

# build image 
#gcloud builds submit metrics-exporter --pack image=gcr.io/$PROJECT_ID/metric-exporter-image
gcloud builds submit metrics-exporter --config=metrics-exporter/cloudbuild.yaml  --substitutions=_REGION=$REGION


echo "Deploy the Cloud Run Job.."
gcloud beta run jobs deploy metric-exporter \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/main/metric-exporter \
    --set-env-vars=PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python \
    --set-env-vars=PROJECT_ID=$PROJECT_ID \
    --execute-now \
    --max-retries=1 \
    --parallelism=0 \
    --service-account=mql-export-metrics@$PROJECT_ID.iam.gserviceaccount.com \
    --region=$REGION

echo "Enable the Cloud Scheduler api.."
gcloud services enable cloudscheduler.googleapis.com

echo "Deploy the Cloud Scheduler job with a schedule to trigger the Cloud Function once a day.."
#gcloud scheduler jobs create pubsub get_metric_mql \
#--schedule "0 23 * * *" \
#--topic metric_export \
#--location ${REGION} \
#--message-body "Exporting metric..."

gcloud scheduler jobs create http recomendation_job \
  --location $REGION \
  --schedule="0 23 * * *" \
  --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/metric-exporter:run" \
  --http-method POST \
  --oauth-service-account-email $(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")-compute@developer.gserviceaccount.com


gcloud scheduler jobs run get_metric_mql --location ${REGION}

echo "Deployment complete"
