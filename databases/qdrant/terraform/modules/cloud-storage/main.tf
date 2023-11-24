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

# [START gke_qdrant_cloud_storage_bucket]
module "cloud-storage" {
  source  = "terraform-google-modules/cloud-storage/google//modules/simple_bucket"
  version = "~> 5.0"

  name          = "${var.cluster_prefix}-training-docs"
  project_id    = var.project_id
  location      = var.region
  force_destroy = true
}

# use to set permissions with the dynamic SA
module "cloud-storage-iam-bindings" {
  source          = "terraform-google-modules/iam/google//modules/storage_buckets_iam"
  storage_buckets = [module.cloud-storage.name]
  mode = "authoritative"
  bindings = {
    "roles/storage.objectViewer" = ["${module.service-account.iam_email}"]
  }  
  depends_on = [module.cloud-storage, module.service-account.iam_email]
}

module "service-account" {
  source       = "terraform-google-modules/service-accounts/google"
  version      = "~> 3.0"
  project_id   = var.project_id
  names        = ["${var.cluster_prefix}-bucket-access"]
  description  = "Service account to access the bucket with Qdrant training documents"
}

output "bucket_name" {
  value = module.cloud-storage.name
}

output "service_account_name" {
  value = module.service-account.email
}
# [END gke_qdrant_cloud_storage_bucket]

