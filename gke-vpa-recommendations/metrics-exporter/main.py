# Copyright 2023 Google Inc.
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
# limitations under the License.
from datetime import datetime, date
import time
import os
import config
from google.cloud import monitoring_v3
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError

import logging

run_date = datetime.now()
logging.basicConfig(level=config.log_level_mapping.get(config.LOGGING_LEVEL.upper(), logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')
    
def get_gke_metrics(metric_name, query):
    """
    Retrieves Google Kubernetes Engine (GKE) metrics.

    Parameters:
    metric_name (str): The name of the metric to retrieve.
    query: Query configuration for the metric.

    Returns:
    list: List of metrics.
    """
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{config.PROJECT_ID}"
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
     
    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": (seconds - query.window), "nanos": nanos},
        }
    )
    aggregation = monitoring_v3.Aggregation(
        {
            "alignment_period": {"seconds": query.seconds_between_points}, 
            "per_series_aligner": query.per_series_aligner,
            "cross_series_reducer": query.cross_series_reducer,
            "group_by_fields": query.columns,
        }
    )
    rows = []
    try:
        results = client.list_time_series(
        request={
                "name": project_name,
                "filter": f'metric.type = "{query.metric}" AND {config.namespace_filter}',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": aggregation
            }
        )
        logging.info("Building Row")
        
        for result in results: 
            row = {}
            label = result.resource.labels
            metadata = result.metadata.system_labels.fields
            metric_label = result.metric.labels
        
            if "hpa" in metric_name:
                controller_name = metric_label['targetref_name']
                controller_type = metric_label['targetref_kind']
                container_name = metric_label['container_name']
            elif "vpa" in metric_name:               
                controller_name = label['controller_name']
                controller_type = label['controller_kind']
                container_name = metric_label['container_name'] 
            else:
                controller_name = metadata['top_level_controller_name'].string_value
                controller_type = metadata['top_level_controller_type'].string_value
                container_name = label['container_name']
            row = {
                    "run_date": run_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "metric_name": metric_name,
                    "project_id": label['project_id'],
                    "location": label['location'],
                    "cluster_name": label['cluster_name'],
                    "namespace_name": label['namespace_name'], 
                    "controller_name": controller_name,
                    "controller_type": controller_type,
                    "container_name": container_name
                }
            points = []         
            for point in result.points:
                test = {
                        "metric_timestamp": point.interval.start_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                        "metric_value": point.value.double_value or float(point.value.int64_value)
                    }     
                points.append(test)
            row["points_array"] = points
            rows.append(row)
    except GoogleAPICallError as error:
        logging.info(f'Google API call error: {error}')
    except Exception as error:
        logging.info(f'Unexpected error: {error}')
    return rows

    

def write_to_bigquery(rows_to_insert):
    client = bigquery.Client()
    errors = client.insert_rows_json(config.TABLE_ID, rows_to_insert)
    if not errors:
        logging.info(f'Successfully wrote {len(rows_to_insert)} rows to BigQuery table {config.TABLE_ID}.')
    else:
        error_message = "Encountered errors while inserting rows: {}".format(errors)
        logging.error(error_message)
        raise Exception(error_message)     


def run_pipeline():   
    for metric, query in config.MQL_QUERY.items():
        logging.info(f'Retrieving {metric}...')
        rows_to_insert = get_gke_metrics(metric, query)
        if rows_to_insert:
            write_to_bigquery(rows_to_insert)
        else:
            logging.info(f'{metric} unavailable. Skip')
    logging.info("Run Completed")   

if __name__ == "__main__":
    if 'PROJECT_ID' not in os.environ or not os.environ['PROJECT_ID']:
        logging.info("Please set the 'PROJECT_ID' environment variable.")
    else:
        run_pipeline()