#!/usr/bin/env bash

echo "*********************************"
echo "Initializing variables"
echo "*********************************"
# Replace the following with values for your own  project.
export PROJECT_ID="<YOUR_PROJECT_ID>"
export REGION="<YOUR_REGION>"
export ZONE="<YOUR_ZONE>"

export CLUSTER_ID="batch-aiml"
export AR_REPO_ID="batch-aiml-docker-repo"
export FILESTORE_ID="batch-aiml-filestore"

echo "PROJECT_ID=${PROJECT_ID}"
echo "CLUSTER_ID=${CLUSTER_ID}"
echo "AP_REPO_ID=${AR_REPO_ID}"
echo "FILESTORE_ID=${FILESTORE_ID}"
echo "REGION=${REGION}"
echo "ZONE=${ZONE}"
echo "*********************************"
