# google_client_config and kubernetes provider must be explicitly specified like the following.
data "google_client_config" "default" {}

module "network" {
  source     = "../modules/network"
  project_id = var.project_id
}

module "gke-db1-autopilot" {
  source                     = "../modules/beta-autopilot-private-cluster"
  project_id                 = var.project_id
  name                       = "cluster-db1"
  kubernetes_version         = "1.25" # Will be ignored if use "REGULAR" release_channel
  region                     = "us-central1"
  regional                   = true
  zones                      = ["us-central1-a", "us-central1-b", "us-central1-c"]
  network                    = module.network.network_name
  subnetwork                 = module.network.primary_subnet_name
  ip_range_pods              = "ip-range-pods-db1"
  ip_range_services          = "ip-range-svc-db1"
  horizontal_pod_autoscaling = true
  # release_channel                 = "REGULAR" # Default version is 1.22 in REGULAR so commented it out to specify V1.24 via var.kubernetes_version
  enable_vertical_pod_autoscaling = true
  enable_private_endpoint         = false
  enable_private_nodes            = true
  master_ipv4_cidr_block          = "172.16.0.0/28"
  create_service_account          = false
  monitoring_enable_managed_prometheus = true
}

module "gke-db2-autopilot" {
  source                     = "../modules/beta-autopilot-private-cluster"
  project_id                 = var.project_id
  name                       = "cluster-db2"
  kubernetes_version         = "1.25" # Will be ignored if use "REGULAR" release_channel
  region                     = "us-west1"
  regional                   = true
  zones                      = ["us-west1-a", "us-west1-b", "us-west1-c"]
  network                    = module.network.network_name
  subnetwork                 = module.network.secondary_subnet_name
  ip_range_pods              = "ip-range-pods-db2"
  ip_range_services          = "ip-range-svc-db2"
  horizontal_pod_autoscaling = true
  # release_channel                 = "REGULAR" # Default version is 1.22 in REGULAR so commented it out to specify V1.24 via var.kubernetes_version
  enable_vertical_pod_autoscaling = true
  enable_private_endpoint         = false
  enable_private_nodes            = true
  master_ipv4_cidr_block          = "172.16.0.16/28"
  create_service_account          = false
  monitoring_enable_managed_prometheus = true
}
