gcloud config set project PROJECT_ID

export PROJECT_ID=$(gcloud config get project) \
&& export PROJECT_NUMBER=$(gcloud projects list --filter="$PROJECT_ID" --format="value(PROJECT_NUMBER)") \
&& export REGION=REGION \
&& export ZONE=$REGION-a \
&& export REPOSITORY_NAME=AR_REPOSITORY_NAME \
&& export MODEL_PATH=MODEL_PATH_NAME \
&& export IMAGE_NAME=CONTAINER_IMAGE_NAME\
&& export IMAGE_TAG=IMAGE_VERSION_TAG \
&& export DISK_IMAGE=DISK_IMAGE_NAME \
&& export CONTAINER_IMAGE=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE_NAME:$IMAGE_TAG \
&& export BUCKET_NAME=gs://BUCKET_FOR_LOGS_NAME/ \
&& export STANDARD_CLUSTER_NAME=STANDARD_CLUSTER_NAME \
&& export STANDARD_NODEPOOL_NAME=STANDARD_NODEPOOL_NAME

echo -n 'YOUR_HUGGINGFACE_USER_NAME' | gcloud secrets create hf-username --data-file=-
echo -n 'YOUR_HUGGINGFACE_USER_TOKEN' | gcloud secrets create hf-token --data-file=-

gcloud artifacts repositories create $REPOSITORY_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="repository to store the container images with the preloaded model weights and the configuration files"

gcloud projects add-iam-policy-binding projects/$PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/compute.instanceAdmin.v1" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

gcloud builds submit \
  --config cloudbuild-image.yaml \
--substitutions=_MODEL_PATH=$MODEL_PATH,_PROJECT_ID=$PROJECT_ID,_REPOSITORY_NAME=$REPOSITORY_NAME,_IMAGE_NAME=$IMAGE_NAME,_REGION=$REGION,_IMAGE_TAG=$IMAGE_TAG

gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME

gsutil mb gs://$BUCKET_NAME

gcloud builds submit --config cloudbuild-disk.yaml --no-source \
--substitutions=_DISK_IMAGE=$DISK_IMAGE,_CONTAINER_IMAGE=$CONTAINER_IMAGE,_BUCKET_NAME=$BUCKET_NAME,_ZONE=$ZONE

gcloud compute images list --no-standard-images

gcloud container clusters create ${STANDARD_CLUSTER_NAME} \
  --project=${PROJECT_ID} \
  --region=${REGION} \
  --workload-pool=${PROJECT_ID}.svc.id.goog \
  --release-channel=rapid \
  --cluster-version=1.28 \
  --num-nodes=1 \
  --enable-image-streaming

gcloud beta container node-pools create ${STANDARD_NODEPOOL_NAME} \
  --accelerator type=nvidia-l4,count=2,gpu-driver-version=latest \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --node-locations=${ZONE} \
  --cluster=${STANDARD_CLUSTER_NAME} \
  --machine-type=g2-standard-24 \
  --num-nodes=1 \
  --disk-size 200 \
  --enable-image-streaming \
 --secondary-boot-disk=disk-image=projects/${PROJECT_ID}/global/images/${DISK_IMAGE},mode=CONTAINER_IMAGE_CACHE

sed "s|<CONTAINER_IMAGE>|$CONTAINER_IMAGE|" model-deployment.yaml | kubectl apply -f -
