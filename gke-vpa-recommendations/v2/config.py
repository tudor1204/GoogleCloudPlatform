# Copyright 2020 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the Licens

from os import environ as env
import logging

# Get the desired logging level from the environment variable
LOGGING_LEVEL = env.get('LOGGING_LEVEL', 'INFO')
SERVICE_ACCOUNT = env.get('SERVICE_ACCOUNT','default')

# Map the environment variable value to the corresponding logging level
log_level_mapping = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Replace the values as needed
PROJECT_ID = env.get('PROJECT_ID')
BIGQUERY_DATASET = env.get('BIGQUERY_DATASET','data')
BIGQUERY_TABLE = env.get('BIGQUERY_TABLE','gke_metrics')
BIGQUERY_LOCATION = env.get('BIGQUERY_LOCATION','us-central1')
TABLE_ID = f'{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}'

assert env.get('PROJECT_ID') != None, "PROJECT_ID is not set or empty. Please set a valid value"

# IMPORTANT: to guarantee successfully retriving data, please use a time window greater than 5 minutes
METRIC_PERIOD = env.get('METRIC_PERIOD', '2w') 
VPA_FILTER = "(resource.namespace_name !~ '(kube|istio|gatekeeper|gke|gmp|gke-gmp|kueue)-system')"
MQL_FILTER = "(resource.namespace_name !~ '(kube|istio|gatekeeper|gke|gmp|gke-gmp|kueue)-system')" 
GKE_GROUP_BY_COLUMNS = '[resource.project_id, resource.location, resource.cluster_name, resource.namespace_name, metadata.system_labels.top_level_controller_name, metadata.system_labels.top_level_controller_type, resource.container_name]'
SCALE_GROUP_BY_COLUMNS = '[resource.project_id, resource.location, resource.cluster_name, resource.namespace_name, resource.controller_name, resource.controller_kind, metric.container_name]'

MQL_QUERY = {
"replica_count":
f"""
fetch k8s_container
| metric 'kubernetes.io/container/cpu/core_usage_time'
| filter {MQL_FILTER}
| align rate(5m)
| every 5m
| group_by {GKE_GROUP_BY_COLUMNS }, [row_count: row_count()]
"""
,
"memory_request_utilization_max":
f"""
fetch k8s_container
| metric 'kubernetes.io/container/memory/request_utilization'
| filter
    {MQL_FILTER}
     && metric.memory_type == 'non-evictable' &&  metadata.system_labels.state == 'ACTIVE'
| group_by {METRIC_PERIOD}, [value_request_utilization_max: max(value.request_utilization)]
| every {METRIC_PERIOD}
| group_by
    {GKE_GROUP_BY_COLUMNS },
    [value_request_utilization_max: max(value_request_utilization_max)]
| scale '%'
"""
,
"memory_limit_utilization_max":
f"""
fetch k8s_container
| metric 'kubernetes.io/container/memory/limit_utilization'
| filter
    {MQL_FILTER}
     && metric.memory_type == 'non-evictable' && metadata.system_labels.state == 'ACTIVE'
| group_by {METRIC_PERIOD}, [value_limit_utilization_max: max(value.limit_utilization)]
| every {METRIC_PERIOD}
| group_by
    {GKE_GROUP_BY_COLUMNS },
    [value_limit_utilization_max: max(value_limit_utilization_max)]
| scale '%'
"""
,
"cpu_request_utilization_mean":
f"""
fetch k8s_container
| metric 'kubernetes.io/container/cpu/request_utilization'
| filter {MQL_FILTER} && metadata.system_labels.state == 'ACTIVE'
| group_by {METRIC_PERIOD}, [value_request_utilization_mean: mean(value.request_utilization)]
| every {METRIC_PERIOD}
| group_by
    {GKE_GROUP_BY_COLUMNS },
    [value_request_utilization_mean_aggregate:
       mean(value_request_utilization_mean)]
| scale '%'
"""
,
"cpu_limit_utilization_max":
f"""
fetch k8s_container
| metric 'kubernetes.io/container/cpu/limit_utilization'
| filter {MQL_FILTER} &&  metadata.system_labels.state == 'ACTIVE'
| group_by {METRIC_PERIOD}, [value_limit_utilization_max: max(value.limit_utilization)]
| every {METRIC_PERIOD}
| group_by
    {GKE_GROUP_BY_COLUMNS },
    [value_limit_utilization_max_aggregate:
       max(value_limit_utilization_max)]
| scale '%'
"""
,
"memory_max_used_mib":
f"""
fetch k8s_container
| metric 'kubernetes.io/container/memory/used_bytes'
| filter {MQL_FILTER} &&   metric.memory_type == 'non-evictable'
  | group_by {METRIC_PERIOD}, [value_used_bytes_max: max(value.used_bytes)]
  | every {METRIC_PERIOD}
  | group_by {GKE_GROUP_BY_COLUMNS }, [value_used_bytes_max_max: aggregate(value_used_bytes_max)]
  | scale 'MiBy' 
"""
,
"memory_requested_mib":
f"""
fetch k8s_container
| metric 'kubernetes.io/container/memory/request_bytes'
| filter {MQL_FILTER} &&  metadata.system_labels.state == 'ACTIVE'
  | group_by 5m, [value_request_bytes_mean: mean(value.request_bytes)]
  | every 5m
  | group_by
      {GKE_GROUP_BY_COLUMNS },
      [value_request_bytes_mean_mean: mean(value_request_bytes_mean)]
| scale 'MiBy' 
"""
,
"memory_limit_mib":
f"""
fetch k8s_container
| metric 'kubernetes.io/container/memory/limit_bytes'
| filter {MQL_FILTER} &&  metadata.system_labels.state == 'ACTIVE'
  | group_by 5m, [value_limit_bytes_mean: mean(value.limit_bytes)]
  | every 5m
  | group_by
      {GKE_GROUP_BY_COLUMNS },
      [value_limit_bytes_mean_mean: mean(value_limit_bytes_mean)]
| scale 'MiBy'
"""
,

"cpu_mcore_usage":
f"""
fetch k8s_container
| filter {MQL_FILTER} &&  metadata.system_labels.state == 'ACTIVE'
| metric 'kubernetes.io/container/cpu/core_usage_time'
| align rate(5m)
| every 5m
| group_by
    {GKE_GROUP_BY_COLUMNS }, [value_core_usage_aggregate: aggregate(value.core_usage_time)]
| window {METRIC_PERIOD}
| scale 'ms/s'
"""
,
"cpu_requested_mcores":
f"""
fetch k8s_container
| filter
    {MQL_FILTER} && metadata.system_labels.state == 'ACTIVE'
| metric 'kubernetes.io/container/cpu/request_cores'
    | group_by 5m, [value_request_cores_mean: mean(value.request_cores)]
    | every 5m
    | group_by
        {GKE_GROUP_BY_COLUMNS },
        [value_request_bytes_mean_mean: mean(value_request_cores_mean)]
| mul 1000
"""
,
"cpu_limit_mcores":
f"""
fetch k8s_container
| filter
    {MQL_FILTER} &&  metadata.system_labels.state == 'ACTIVE'
| metric 'kubernetes.io/container/cpu/limit_cores'
    | group_by 5m, [value_limit_cores_mean: mean(value.limit_cores)]
    | every 5m
    | group_by
        {GKE_GROUP_BY_COLUMNS },
        [value_limit_bytes_mean_mean: mean(value_limit_cores_mean)]
| mul 1000
"""
}

BASE_URL = "https://monitoring.googleapis.com/v3/projects"
QUERY_URL = f"{BASE_URL}/{PROJECT_ID}/timeSeries:query"