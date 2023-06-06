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

resource "google_bigquery_dataset" "dataset" {
  dataset_id  = local.bigquery_dataset
  description = "GKE container recommendations dataset"
  location    = var.region
  labels      = local.resource_labels
}

resource "google_bigquery_table" "gke_metrics" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = local.bigquery_table
  description         = "GKE system and scale metrics"
  deletion_protection = false
  
  time_partitioning {
    type = "DAY"
  }

  labels = local.resource_labels

  schema = <<EOF
[
    {
      "name": "metric",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "project_id",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "location",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "cluster_name",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "namespace_name",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "controller_name",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "controller_type",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "container_name",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "point_value",
      "type": "FLOAT",
      "mode": "REQUIRED"
    }
    ,
    {
      "name": "metric_timestamp",
      "type": "TIMESTAMP",
      "mode": "REQUIRED"
    }
  ]
EOF
 
}

resource "google_bigquery_table" "workload_recommendation_view" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = local.bigquery_recommendations_view
  deletion_protection=false
  view {
    query = templatefile("../recommendation_query.sql", { project_id = var.project_id, table_dataset = local.bigquery_dataset, table_id = local.bigquery_table })
    use_legacy_sql = false
  }
  labels = local.resource_labels
  depends_on = [google_bigquery_table.gke_metrics]
}
resource "google_bigquery_table" "workloads_at_risk_view" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = local.bigquery_workloads_at_risk_view
  deletion_protection=false
  view {
    query = templatefile("../workloads_at_risk_query.sql", { project_id = var.project_id, table_dataset = local.bigquery_dataset, table_id = local.bigquery_recommendations_view})
    use_legacy_sql = false
  }
  labels = local.resource_labels  
}

