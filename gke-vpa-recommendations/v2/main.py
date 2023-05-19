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
# limitations under the License.

import logging
import config
import requests
import subprocess
from google.cloud import bigquery
import sys
import math

token = None

METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/"
METADATA_HEADERS = {"Metadata-Flavor": "Google"}


logging.basicConfig(level=config.log_level_mapping.get(config.LOGGING_LEVEL.upper(), logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')

def get_access_token_from_meta_data():
    url = '{}instance/service-accounts/{}/token'.format(
        METADATA_URL, config.SERVICE_ACCOUNT)
    
    try:
        # Request an access token from the metadata server.
        r = requests.get(url, headers=METADATA_HEADERS)
        r.raise_for_status()

        # Extract the access token from the response.
        token = r.json()['access_token']
        return token
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving access token: {e}")


def get_access_token_from_gcloud(force=False):
    url = '{}instance/service-accounts/{}/token'.format(
        METADATA_URL, config.SERVICE_ACCOUNT)

    try:
        # Request an access token from the metadata server.
        r = requests.get(url, headers=METADATA_HEADERS)
        r.raise_for_status()

        # Extract the access token from the response.
        token = r.json()['access_token']
        return token
    except requests.exceptions.RequestException as e:
        logging.error(f"Error retrieving access token: {e}")
        return None


def get_mql_result(token, query, pageToken):
    q = f'{{"query":"{query}", "pageToken":"{pageToken}"}}' if pageToken else f'{{"query": "{query}"}}'

    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {token}"}
    try:
        response = requests.post(config.QUERY_URL, data=q, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error in MQL request: {e}")
        return None


def extract_rows_from_results(metric, results):
    """ Build a list of JSON object rows to insert into BigQuery
        This function may fan out the input by writing 1 entry into BigQuery for every point,
        if there is more than 1 point in the timeseries
    """ 
    rows = []
    metric_value_type = results["timeSeriesDescriptor"]["pointDescriptors"][0]["valueType"]
 
    for data in results["timeSeriesData"]:    
        label_values = data["labelValues"]   
        label = [label_value["stringValue"] for label_value in label_values]
        point_data = data["pointData"][0]
        point_data_values = point_data["values"][0]
        starttime = point_data["timeInterval"]["startTime"]     

        if metric_value_type == "DOUBLE":
            value = point_data_values["doubleValue"]
        else:
            value = point_data_values["int64Value"]
        
        # Add the recommendation buffer
        if "memory_request_max_recommendations_mib" in metric:
            value += (value * config.MEMORY_RECOMMENDATION_BUFFER)
        if "cpu_request_recommendations" in metric:
            value += value * config.CPU_RECOMMENDATION_BUFFER          
        
        row = {
            "metric": metric,
            "project_id": label[0],
            "location": label[1],
            "cluster_name": label[2],
            "namespace_name": label[3], 
            "controller_name": label[4],
            "controller_type": label[5],
            "container_name": label[6],
            "point_value": math.ceil(value),
            "metric_timestamp": starttime 
        }
        rows.append(row)        
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

     
def save_to_bq(token):    
    for metric, query in config.MQL_QUERY .items():        
        pageToken = ""
        while (True):
            result = get_mql_result(token, query, pageToken)
            if result.get("timeSeriesDescriptor"):
                row = extract_rows_from_results(metric, result)
                write_to_bigquery(row)
            pageToken = result.get("nextPageToken")
            if not pageToken:
                logging.info("No more data retrieved")
                break
    logging.info("Run Completed")

def main():
    token = get_access_token_from_gcloud() 
    if token is None:
        logging.error("Failed to retrieve access token. Exiting...")
        return
    save_to_bq(token) 

if __name__ == '__main__':
    main()