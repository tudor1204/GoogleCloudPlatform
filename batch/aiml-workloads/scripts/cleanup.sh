#!/usr/bin/env bash

source scripts/variables.sh

echo "*********************************"
echo "Deleting GCP resources"
echo "*********************************"

# Delete the Artifact Repository repo
gcloud artifacts repositories delete ${AR_REPO_ID} --location=${REGION}
echo "Artifact Repository repository '${AR_REPO_ID}' deleted."

# Delete the GKE cluster
gcloud container clusters delete ${CLUSTER_ID} \
    --project=${PROJECT_ID} --zone=${ZONE}
echo "GKE cluster '${CLUSTER_ID}' deleted."

# Delete the Filestore instance
gcloud filestore instances delete ${FILESTORE_ID} --zone=${ZONE}
echo "Filestore instance '${FILESTORE_ID}' deleted."
