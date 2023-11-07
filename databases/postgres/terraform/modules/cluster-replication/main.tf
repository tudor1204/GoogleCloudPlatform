# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gke_postgres_standard_private_regional_cluster]
module "postgres_cluster" {
  source                   = "terraform-google-modules/kubernetes-engine/google//modules/private-cluster"
  version                  = "~> 29.0"
  project_id               = var.project_id
  name                     = "${var.cluster_prefix}-cluster"
  regional                 = true
  region                   = var.region
  network                  = var.network
  subnetwork               = var.subnetwork
  ip_range_pods            = "k8s-pod-range"
  ip_range_services        = "k8s-service-range"
  create_service_account   = true
  enable_private_endpoint  = false
  enable_private_nodes     = true
  master_ipv4_cidr_block   = var.master_ipv4_cidr_block
  network_policy           = true
  logging_enabled_components = ["SYSTEM_COMPONENTS","WORKLOADS"]
  monitoring_enabled_components = ["SYSTEM_COMPONENTS"]
  enable_cost_allocation = true
  initial_node_count = 1

  cluster_dns_domain   = "${var.cluster_prefix}.local"
  cluster_dns_provider = "CLOUD_DNS"
  cluster_dns_scope    = "VPC_SCOPE"

  cluster_resource_labels = {
    name      = "${var.cluster_prefix}-cluster"
    component = "${var.cluster_prefix}-operator"
  }

  monitoring_enable_managed_prometheus = true
  gke_backup_agent_config = true
 
  node_pools = [
    {
      name            = "pool-postgres"
      disk_size_gb    = 20
      disk_type       = "pd-standard"
      autoscaling     = true
      min_count       = 1
      max_count       = 2
      max_surge       = 1
      max_unavailable = 0
      machine_type    = "e2-standard-2"
      auto_repair     = true
    }
  ]
  node_pools_labels = {
    all = {}
    pool-postgres = {
      "app.stateful/component" = "postgres-operator"
    } 
  }
  node_pools_taints = {
    all = []
    pool-redis = [
      {
        key    = "app.stateful/component"
        value  = "postgres-operator"
        effect = "NO_SCHEDULE"
      }
    ]
  }
  gce_pd_csi_driver = true
}
# [END gke_postgres_standard_private_regional_cluster]

