#Copyright 2022 Google LLC

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

# google_client_config and kubernetes provider must be explicitly specified like the following.
data "google_client_config" "default" {}

module "network" {
  source     = "../modules/network"
  project_id = var.project_id
}
# [START gke_autopilot_private_regional_primary_cluster]
module "gke-us-central1-autopilot" {
  source                          = "../modules/beta-autopilot-private-cluster"
  project_id                      = var.project_id
  name                            = "gke-kafka-us-central1"
  # release_channel                 = "REGULAR" # Default version is 1.22 in REGULAR so commented it out to specify V1.24 via var.kubernetes_version
  region                          = "us-central1"
  regional                        = true
  zones                           = ["us-central1-a", "us-central1-b", "us-central1-c"]
  network                         = module.network.network_name
  subnetwork                      = module.network.primary_subnet_name
  ip_range_pods                   = "ip-range-pods-us-central1"
  ip_range_services               = "ip-range-svc-us-central1"
  horizontal_pod_autoscaling      = true
  enable_vertical_pod_autoscaling = true
  enable_private_endpoint         = false
  enable_private_nodes            = true
  master_ipv4_cidr_block          = "172.16.0.0/28"
  create_service_account          = false
}
# [END gke_autopilot_private_regional_primary_cluster]
# [START gke_autopilot_private_regional_backup_cluster]
module "gke-us-west1-autopilot" {
  source                          = "../modules/beta-autopilot-private-cluster"
  project_id                      = var.project_id
  name                            = "gke-kafka-us-west1"
  # release_channel                 = "REGULAR" # Default version is 1.22 in REGULAR so commented it out to specify V1.24 via var.kubernetes_version
  region                          = "us-west1"
  regional                        = true
  zones                           = ["us-west1-a", "us-west1-b", "us-west1-c"]
  network                         = module.network.network_name
  subnetwork                      = module.network.secondary_subnet_name
  ip_range_pods                   = "ip-range-pods-us-west1"
  ip_range_services               = "ip-range-svc-us-west1"
  horizontal_pod_autoscaling      = true
  enable_vertical_pod_autoscaling = true
  enable_private_endpoint         = false
  enable_private_nodes            = true
  master_ipv4_cidr_block          = "172.16.0.16/28"
  create_service_account          = false
}
# [END gke_autopilot_private_regional_backup_cluster]
