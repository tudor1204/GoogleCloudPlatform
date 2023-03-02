
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

echo "Deploy the Cloud Function.."

gcloud functions deploy mql-export-metric \
--source metrics-exporter \
--region us-central1 \
--trigger-topic metric_export \
--runtime python39 \
--ingress-settings=internal-and-gclb \
--memory 2048MB \
--timeout 540s \
--entry-point export_metric_data \
--set-env-vars PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python \
--set-env-vars PROJECT_ID=$PROJECT_ID
--service-account=mql-export-metrics@$PROJECT_ID.iam.gserviceaccount.com

echo "Enable the Cloud Scheduler api.."
gcloud services enable cloudscheduler.googleapis.com

echo "Deploy the Cloud Scheduler job with a schedule to trigger the Cloud Function once a day.."
gcloud scheduler jobs create pubsub get_metric_mql \
--schedule "0 23 * * *" \
--topic metric_export \
--location us-central1 \
--message-body "Exporting metric..."

gcloud scheduler jobs run get_metric_mql --location us-central1

echo "Deployment complete"
