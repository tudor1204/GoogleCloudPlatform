export PROJECT_ID=$(gcloud config get project) \
&& export REGION=us-central1 \
&& export REPOSITORY_NAME=kfilatau-test-repo \
&& export IMAGE_NAME=gemma-2b-it-test-cropped-v2\
&& export MODEL_PATH=gemma-2b-it

gcloud builds submit --config cloudbuild-disk.yaml \
  --no-source
#  --service-account "projects/$PROJECT_ID/serviceAccounts/compute-default@or2-msq-go2-gkes-t1iylu.iam.gserviceaccount.com"

gcloud builds submit \
  --config cloudbuild-image.yaml \
  --substitutions=_MODEL_PATH=$MODEL_PATH,_PROJECT_ID=$PROJECT_ID,_REPOSITORY_NAME=$REPOSITORY_NAME,_IMAGE_NAME=$IMAGE_NAME
#  --service-account "projects/$PROJECT_ID/serviceAccounts/compute-default@or2-msq-go2-gkes-t1iylu.iam.gserviceaccount.com"


export PJCT_NMBR=$(gcloud projects list --filter="$PROJECT_ID" --format="value(PROJECT_NUMBER)")
gcloud projects add-iam-policy-binding projects/$PROJECT_ID \
    --member="serviceAccount:$PJCT_NMBR@cloudbuild.gserviceaccount.com" \
    --role="roles/compute.instanceAdmin" \
    --condition=None
gcloud projects add-iam-policy-binding projects/$PROJECT_ID \
    --member="serviceAccount:$PJCT_NMBR@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

