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
import time
import config
import asyncio
import logging
import utils
import warnings

from google.cloud import monitoring_v3
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError

warnings.filterwarnings(
    "ignore",
    "Your application has authenticated using end user credentials")



async def get_gke_metrics(metric_name, query, namespace, start_time, client):
    """
    Retrieves Google Kubernetes Engine (GKE) metrics.

    Parameters:
    metric_name (str): The name of the metric to retrieve.
    query: Query configuration for the metric.

    Returns:
    list: List of metrics.
    """
    interval = utils.get_interval(start_time, query.window)
    aggregation = utils.get_aggregation(query)
    project_name = utils.get_request_name()

    rows = []
    try:
        results = client.list_time_series(
            request={
                "name": project_name,
                "filter": f'metric.type = "{query.metric}" AND resource.label.namespace_name = {namespace}',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": aggregation})

        logging.info(f"Building Row of metric results")

        for result in results:
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
                "run_date": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
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
                    "metric_value": point.value.double_value or float(
                        point.value.int64_value)}
                points.append(test)
            row["points_array"] = points
            rows.append(row)
    except GoogleAPICallError as error:
        logging.info(f'Google API call error: {error}')
    except Exception as error:
        logging.info(f'Unexpected error: {error}')
    return rows


async def write_to_bigquery(client, rows_to_insert):
    errors = client.insert_rows_json(config.TABLE_ID, rows_to_insert)
    if not errors:
        logging.info(
            f'Successfully wrote {len(rows_to_insert)} rows to BigQuery table {config.TABLE_ID}.')
    else:
        error_message = "Encountered errors while inserting rows: {}".format(
            errors)
        logging.error(error_message)
        raise Exception(error_message)


async def run_pipeline(namespace, client, bqclient, start_time):
    for metric, query in config.MQL_QUERY.items():
        logging.info(f'Retrieving {metric} for namespace {namespace}...')
        rows_to_insert = await get_gke_metrics(metric, query, namespace, start_time, client)

        if rows_to_insert:
            await write_to_bigquery(bqclient, rows_to_insert)
        else:
            logging.info(f'{metric} unavailable. Skip')

    logging.info("Run Completed")

def get_namespaces(client, start_time):
    namespaces = set()
    query = config.NS_QUERY

    interval = utils.get_interval(start_time, query.window)
    aggregation = utils.get_aggregation(query)
    project_name = utils.get_request_name()

    try:
        results = client.list_time_series(
            request={
                "name": project_name,
                "filter": f'metric.type = "{query.metric}" AND {config.namespace_filter}',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.HEADERS,
                "aggregation": aggregation})

        logging.info("Building Row of Namespace results")
        for result in results:
            label = result.resource.labels
            namespaces.add(label['namespace_name'])
        return list(namespaces)

    except GoogleAPICallError as error:
        logging.error(f'Google API call error: {error}')
    except Exception as error:
        logging.error(f'Unexpected error: {error}')
    return list(namespaces)


if __name__ == "__main__":
    utils.setup_logging()
    start_time = time.time()

    try:
        client = monitoring_v3.MetricServiceClient()
        bqclient = bigquery.Client()
    except Exception as error:
        logging.error(f'Google client connection error: {error}')

    monitor_namespaces = get_namespaces(client, start_time)
    namespace_count = len(monitor_namespaces)

    logging.debug(f"Discovered {namespace_count} namespaces to query")
    if (namespace_count > 0):
        for namespace in monitor_namespaces:
            asyncio.run(
                run_pipeline(
                    namespace,
                    client=client,
                    bqclient=bqclient,
                    start_time=start_time))
    else:
        logging.error("Monitored Namespace list is zero size, end Job")
