# Terraform to provision GKE and Artifact Registry

## Feature List
The following resources will be configured by terraform:
1. Notification Channel
1. Alert Policy: `db_max_transaction` 
   Monitors the Max Lag of transaction in seconds, an alert will be triggered if the value is greater than 10.
1. Alert Policy: `db_pod_up`
   Monitors the status of DB pod, 0 means a pod is down so an alert will be triggered.

## Prerequisites and Assumptions
* Done initialization of the project and gcloud CLI following the instructions in `{ROOT}/README.md`

## Usage
```
terraform init
terraform plan -var project_id=$PROJECT_ID -var email_address='Your_Email'
terraform apply -var project_id=$PROJECT_ID -var email_address='Your_Email'
```
## Clean up
**NOTE:** Be very careful when destroying any resource, not recommended for production!
```
# Destroy everything
terraform destroy -var project_id=$PROJECT_ID -var email_address='Your_Email'
```