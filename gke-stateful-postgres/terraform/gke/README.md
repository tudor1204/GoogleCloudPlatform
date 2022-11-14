# Terraform to provision GKE and Artifact Registry

## Feature List
* Enable apis
* Create Artifact Registry, please import if already exists.
* Provision VPC network and subnets
* Create the source and target GKE clusters, each has two node pools provisioned in the central and west subnets
* Setup labels and taints on these GKE clusters, which will be used by the helm chart to distribute the db Pods into different nodes in the dedicated node pool
* Enable Workload Identity
* Enable `Backup for GKE`
* Create Service Account for GKE binding with Artifact Registry

## Prerequisites and Assumptions
* Done initialization of the project and gcloud CLI following the instructions in `{ROOT}/README.md`

## Usage
```
terraform init
terraform plan -var project_id=$PROJECT_ID
terraform apply -var project_id=$PROJECT_ID
```
## Clean up
**NOTE:** Be very careful when destroying any resource, not recommended for production!
```
# Destroy everything
terraform destroy -var project_id=$PROJECT_ID

# Destroy GKE clusters
terraform destroy \
-var project_id=$PROJECT_ID \
-target='module.gke-db2.google_container_cluster.primary' \
-target='module.gke-db1.google_container_cluster.primary'
```

## Highlights and Tips

### How to make sure the DB Pods will be scheduled onto the specific node pool? 
* Config `nodeSelector` or `nodeAffinity` in the DB manifest, find the example code block of `nodeAffinityPreset` in `values.yaml` in the helm chart folder
* Apply specified labels for the target node pool, refer to the code block `node_pools_labels` in `main.tf` 

### How to avoid non-DB Pods to be scheduled onto the DB node pool?
* Config `tolerations` in the DB manifest, find the example code block of `tolerations` in `values.yaml` in the helm chart folder
* Apply the specified labels for the target node pool, refer to the code block `node_pools_taints` in `main.tf` 

### Import an existing resource
If an Artifact Registry already exists, you'll need import it like below commands:
```
gcloud artifacts repositories describe main --location us | grep name

terraform import google_artifact_registry_repository.main projects/$PROJECT_ID/locations/us/repositories/main
```
