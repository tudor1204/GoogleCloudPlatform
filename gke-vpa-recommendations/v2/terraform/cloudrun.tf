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


resource "google_cloud_run_v2_job" "metric_exporter" {
  name         = local.application_name
  location     = var.region
  launch_stage = "BETA"
  
  template {
    task_count  = 1
    parallelism = 0
    labels      = local.resource_labels
    template {
      service_account = google_service_account.service_account.email
      timeout         = "3600s"
      containers {
        image = "us-docker.pkg.dev/${var.project_id}/docker-repo/recommendations-image:tag1"
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        env {
            name = "LOGGING_LEVEL"
            value = "INFO"
        }
        env {
            name = "SERVICE_ACCOUNT"
            value = "default"
        }
        env {
            name = "BIGQUERY_DATASET"
            value = local.bigquery_dataset
        }
        env {
            name = "BIGQUERY_TABLE"
            value = local.bigquery_table
        }
        env {
            name = "BIGQUERY_LOCATION"
            value = var.region
        }
        env {
            name = "CPU_RECOMMENDATION_BUFFER"
            value = 0.0
        }
        env {
            name = "MEMORY_RECOMMENDATION_BUFFER"
            value = 0.10
        }
        env {
            name = "METRIC_PERIOD"
            value = "2w"
        }

        resources {
          limits = {
            memory = local.run_memory
            cpu = local.run_cpu
          }
        }
      }
    }
  }
}

