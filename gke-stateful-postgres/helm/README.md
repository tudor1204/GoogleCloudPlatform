# Deploy Postgresql via helm chart: Primary with Read Replica

`bitnami/postgresql` is used in this test, refer to below guide for parameters:
https://artifacthub.io/packages/helm/bitnami/postgresql

## Key Features
* Deploy statefulsets for one Primary with two Read Replicas
* Config `ProtectedApplication` as predefined backup scope

## Prerequisites:
* Monitoring has been setup successfully

  Refer to `<ROOT>/monitoring/helm/monitoring-stack-bootstrap/README.md` to setup the environment.

  Verification by Prometheus Query
  ```
  up{cluster=~"cluster-db1|cluster-db2"}
  ```

## Deploy Steps
1. Update `values.yaml`, make sure each value matches the actual environment.

1. Deploy the helm realease
    ```
    # resolve and fetch chart dependencies.
    kubectx $SOURCE_CLUSTER  
    helm dependency update
    export NAMESPACE=postgresql

    # make sure the chart renders successfully.
    helm -n $NAMESPACE template postgresql . \
    --set global.imageRegistry="us-docker.pkg.dev/$PROJECT_ID/main"    

    # Install the chart (releasename=postgresql)
    kubectl create namespace $NAMESPACE
    helm -n $NAMESPACE upgrade --install postgresql . \
    --set global.imageRegistry="us-docker.pkg.dev/$PROJECT_ID/main"
    ```
1. Check the Pods
    ```  
    kubectl get po -n $NAMESPACE -o wide -w

    NAME                                               READY   STATUS    RESTARTS   AGE   IP            NODE                                     
    postgresql-postgresql-ha-pgpool-799497b4b9-rf8pd   1/1     Running   0          18m   192.168.0.3   gke-cluster-db1-pool-sys1-5898093d-tbjx
    postgresql-postgresql-ha-postgresql-0              2/2     Running   0          18m   192.168.5.2   gke-cluster-db1-pool-db1-b880fbb2-xclt
    postgresql-postgresql-ha-postgresql-1              2/2     Running   0          18m   192.168.3.2   gke-cluster-db1-pool-db1-0c009233-16w6
    ```
## Verify DB metrics on Prometheus ui
  ```
  pg_up
  pg_exporter_scrapes_total

  # Summarize job names with count
  sort_desc(count by(job) ({__name__!=""}))

  # Show all metrics for a job
  {__name__=~".+", job="postgresql-primary-metrics"}
  {__name__!="", job="postgresql-primary-metrics"}
  ```

## Guide for Beginner of Helm
  Typical usages of Helm
  ```
  # Add Bitami repo to your helm
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm repo update

  # Find the charts for postgres
  helm search repo | grep postgres

  NAME                 	CHART VERSION	APP VERSION	DESCRIPTION
  bitnami/postgresql   	11.6.25      	14.4.0     	PostgreSQL (Postgres)
  bitnami/postgresql-ha	9.2.8        	14.4.0     	This PostgreSQL cluster solution

  # list all the versions you can use from the repo
  helm search repo -l bitnami/postgresql-ha

  # download the manifest for a named release
  helm get manifest bitnami/postgresql-ha

  # Render chart templates locally and display the output.
  helm -n $NAMESPACE template postgresql .
      
  # list releases across all namespaces
  helm list -A
  ```

## Troubleshooting Prometheus monitoring for PostgreSQL

### Save the rendered Helm chart to a local file
```
  helm -n $NAMESPACE template \
  --set global.imageRegistry="us-docker.pkg.dev/$PROJECT_ID/main" \
   postgresql . > $HOME/helm-all-db-mon.yml
```

## Verify the metrics traffic workflow
Traffic flow of monitoring metrics for PostgreSQL

Target Pod 
* => Exporter sidecar (tcp:9187)
* => Metrics Service (tcp:9187) eg: postgresql-primary-metrics
* => Prometheus scrape(ServiceMonitor) eg: postgresql-primary postgresql-read
* => Kind Prometheus collects monitor targets by label like ServiceMonitor selector
* => The Prometheus Operator watches Custom Resources (here ServiceMonitor) and configures the Prometheus instance (kind) with the corresponding scrape config
* => The Pod Prometheus collects metrics as the above defined scrape config (tcp:9090)
* => The service Prometheus exposes the metrics endpoint (tcp:9090)
* => The metrics is saved at Monarch
* => Metrics is available at Cloud Monitoring or PromQL Query 
* => Metrics gets presented via Dashboard on GCP

## Verify the service and traffic flow
### 1: Check the metrics endpoint on Exporter sidecar
```
kubectl exec -it -n postgresql postgresql-primary-0 -c metrics -- /bin/bash
!@postgresql-0:/opt/bitnami/postgres-exporter$ curl localhost:9187/metrics
```
### 2: Check the service endpoints
```
# get the cluster ip of metrics service
kubectl get svc -n postgresql
NAME                         TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
postgresql-primary-metrics   ClusterIP   192.168.79.114   <none>        9187/TCP   18m
postgresql-read-metrics      ClusterIP   192.168.85.195   <none>        9187/TCP   18m
...
kubectl describe svc -n postgresql postgresql-read-metrics
Endpoints:         192.168.0.2:9187,192.168.1.2:9187
```
### 3: Check prometheus service
```
kubectl port-forward -n monitoring prometheus-monitoring-stack-kube-prom-prometheus-0 9090:9090
# View at browser, make sure the db servicemonitor are collected like below 
http://localhost:9090/targets
serviceMonitor/monitoring/monitoring-stack-prometheus-node-exporter/0 (6/6 up)
serviceMonitor/monitoring/postgresql-primary/0 (1/1 up)
serviceMonitor/monitoring/postgresql-read/0 (2/2 up)
```