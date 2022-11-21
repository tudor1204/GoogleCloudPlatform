# Deploy Postgresql via helm chart: Primary with Read Replica

`bitnami/postgresql-ha` is used to deploy PostgreSQL. Refer to below guide for parameters:
https://artifacthub.io/packages/helm/bitnami/postgresql-ha.

## Additional Features within `postgresql-bootstrap` chart.
* Configure `ProtectedApplication` as predefined backup scope.
* Configure custom `StorageClass` with `Retain` `reclaimPolicy`.
* Configure a `PodMonitoring` resource to enable Google Managed Prometheus to scrape metrics from `postgresql-exporter`.

## Deploy Steps

```
export PROJECT_ID=<your-project>
kubectl create namespace postgresql
helm dependency update

# Inspect the charts that Helm will install
helm -n postgresql template postgresql . \
--set global.imageRegistry="us-docker.pkg.dev/$PROJECT_ID/main"    

# Install the Helm chart
helm -n postgresql upgrade --install postgresql ./ \
  --set global.imageRegistry=us-docker.pkg.dev/$PROJECT_ID/main
```
