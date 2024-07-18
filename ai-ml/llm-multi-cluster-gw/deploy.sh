#!/bin/sh

# Set up env variables values
# PROJECT_ID="your-project-id"
# REGION_1="us-central1"
# REGION_2="europe-west4"
# HF_TOKEN="your-HuggingFace-API-token"  

PROJECT_NUMBER=$(gcloud projects list \
--filter="$(gcloud config get-value project)" \
--format="value(PROJECT_NUMBER)")

gcloud services enable container.googleapis.com \
    --project=$PROJECT_ID 

# Create terraform.tfvars file 
cat <<EOF >gke-platform/terraform.tfvars
project_id                = "$PROJECT_ID"
enable_autopilot          = true
region_1                  = "$REGION_1"
region_2                  = "$REGION_2"
gpu_pool_machine_type     = "g2-standard-4"
gpu_pool_accelerator_type = "nvidia-l4"
gpu_pool_node_locations_1 = $(gcloud compute accelerator-types list --filter="zone ~ $REGION_1 AND name=nvidia-tesla-a100" --limit=2 --format=json | jq -sr 'map(.[].zone|split("/")|.[8])|tojson')
gpu_pool_node_locations_2 = $(gcloud compute accelerator-types list --filter="zone ~ $REGION_2 AND name=nvidia-l4" --limit=2 --format=json | jq -sr 'map(.[].zone|split("/")|.[8])|tojson')
fleet_project_id          = "$PROJECT_ID"
enable_fleet              = true
gateway_api_channel       = "CHANNEL_STANDARD"
EOF

# Create clusters
terraform -chdir=gke-platform apply --auto-approve

# Get cluster credentials
gcloud container clusters get-credentials llm-cluster-1 \
    --region=$REGION_1 \
    --project=$PROJECT_ID

gcloud container clusters get-credentials llm-cluster-2 \
    --region=$REGION_2 \
    --project=$PROJECT_ID

# Rename cluster contexts
kubectl config rename-context gke_${PROJECT_ID}_us-central1_llm-cluster-1 gke-us
kubectl config rename-context gke_${PROJECT_ID}_europe-west4_llm-cluster-2 gke-eu

# Enable multi-cluster Services in the fleet
gcloud container fleet multi-cluster-services enable \
    --project $PROJECT_ID

#Grant Identity and Access Management (IAM) permissions required by the MCS controller
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[gke-mcs/gke-mcs-importer]" \
    --role "roles/compute.networkViewer" \
    --condition=None \
    --project=$PROJECT_ID


# Enable multi-cluster Gateway in the fleet, choose lm-cluster-1 cluster as config cluster
gcloud container fleet ingress enable \
    --config-membership=projects/$PROJECT_ID/locations/$REGION_1/memberships/llm-cluster-1 \
    --project=$PROJECT_ID


# Grant Identity and Access Management (IAM) permissions required by the multi-cluster Gateway controller
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member "serviceAccount:service-$PROJECT_NUMBER@gcp-sa-multiclusteringress.iam.gserviceaccount.com" \
    --role "roles/container.admin" \
    --condition=None \
    --project=$PROJECT_ID


NAMESPACE=llm

# Deploy workloads in gke-us
kubectl config use-context gke-us
kubectl create ns $NAMESPACE
kubectl create secret generic hf-secret \
  --from-literal=hf_api_token=$HF_TOKEN \
  --dry-run=client -o yaml | kubectl apply --context=gke-us -n $NAMESPACE -f -

kubectl apply -f tgi-2b-it-1.1-us.yaml -n $NAMESPACE
# kubectl apply -f gradio-tgi-us.yaml -n $NAMESPACE
# Deploy serviceExport 
kubectl apply -f export-us.yaml -n $NAMESPACE

# Deploy workloads in gke-eu
kubectl config use-context gke-eu
kubectl create ns  $NAMESPACE


kubectl apply -f secret.yaml -n $NAMESPACE
kubectl apply -f tgi-2b-it-1.1-eu.yaml -n $NAMESPACE
# kubectl apply -f gradio-tgi-eu.yaml -n $NAMESPACE

# Deploy serviceExport 
kubectl apply -f export-eu.yaml -n $NAMESPACE

# Deploy multicluster gateway in config cluster 
kubectl config use-context gke-us
kubectl apply -f gateway.yaml -n $NAMESPACE

sleep 360
kubectl apply -f monitoring.yaml -n $NAMESPACE --context=gke-us
kubectl apply -f monitoring.yaml -n $NAMESPACE --context=gke-eu

