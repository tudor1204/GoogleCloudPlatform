# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
export PROJECT_ID=<your-project-id>

export REGION=us-east1
export ZONE_1=${REGION}-c # You may want to change the zone letter based on the region you selected above

export CLUSTER_NAME=gpu-autoscale
gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"
gcloud config set compute/zone "$ZONE_1"

gcloud container clusters create $CLUSTER_NAME --location ${REGION} \
  --workload-pool ${PROJECT_ID}.svc.id.goog \
  --enable-image-streaming --enable-shielded-nodes \
  --shielded-secure-boot --shielded-integrity-monitoring \
  --enable-ip-alias \
  --node-locations=$REGION-b \
  --workload-pool=${PROJECT_ID}.svc.id.goog \
  --addons GcsFuseCsiDriver   \
  --no-enable-master-authorized-networks \
  --machine-type n2d-standard-4 \
  --cluster-version 1.29 \
  --num-nodes 1 --min-nodes 1 --max-nodes 3 \
  --ephemeral-storage-local-ssd=count=2 \
  --scopes="gke-default,storage-rw"

#TPU:

gcloud container node-pools create $CLUSTER_NAME-tpu \
--location=$REGION --cluster=$CLUSTER_NAME --node-locations=$ZONE_1 \
--machine-type=ct5lp-hightpu-1t --num-nodes=0 --spot --node-version=1.29 \
--ephemeral-storage-local-ssd=count=0 --enable-image-streaming \
--shielded-secure-boot --shielded-integrity-monitoring \
--enable-autoscaling --total-min-nodes 0 --total-max-nodes 2 --location-policy=ANY