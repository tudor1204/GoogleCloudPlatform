resource "google_container_cluster" "primary" {
  addons_config {
    gke_backup_agent_config {
      enabled = true
    }
  }
}
