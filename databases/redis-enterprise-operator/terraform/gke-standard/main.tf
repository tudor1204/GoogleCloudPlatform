#Copyright 2023 Google LLC

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

# create private subnet
module "network" {
  source         = "../modules/network"
  project_id     = var.project_id
  region         = var.region
  cluster_prefix = var.cluster_prefix
}

# [START gke redis enterprise cluster]
module "redis_cluster" {
  source                   = "../modules/cluster"
  project_id               = var.project_id
  region                   = var.region
  cluster_prefix           = var.cluster_prefix
  network                  = module.network.network_name
  subnetwork               = module.network.subnet_name

  node_pools = [
    {
      name            = "pool-rec"
      disk_size_gb    = 50
      disk_type       = "pd-standard"
      autoscaling     = true
      min_count       = 1
      max_count       = 2
      max_surge       = 1
      max_unavailable = 0
      machine_type    = "e2-standard-4"
      auto_repair     = true
      auto_upgrade    = false
      version         = "1.26.7-gke.500"
      
    }
  ]
  node_pools_labels = {
    all = {}
    pool-redis = {
      "app.stateful/component" = "rec"
    }
  }
  node_pools_taints = {
    all = []
  }
}

output "kubectl_connection_command" {
  value       = "gcloud container clusters get-credentials ${var.cluster_prefix}-cluster --region ${var.region}"
  description = "Connection command"
}
# [END gke_streaming_kafka_strimzi_standard_private_regional_cluster]
