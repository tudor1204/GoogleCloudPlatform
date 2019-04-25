# Hello Application with IAP example

> **Note:** This application is a copy of [hello-app](../hello-app) sample.
> See that directory for more details on this sample.

## Build the image
```
$ docker build -t gcr.io/${PROJ}/hello-app-iap:v1 -f Dockerfile  .
$ docker push gcr.io/${PROJ}/hello-app-iap:v1
```

## Deploy the containers
```
$ kubectl apply -f manifests/deployment.yaml
```

## Create secret

Follow the guide: https://cloud.google.com/iap/docs/enabling-kubernetes-howto#oauth-credentials

## Create backendconfig and service

```
kubectl apply -f manifests/backendconfig.yaml
kubectl apply -f manifests/service1.yaml
kubectl apply -f manifests/service2.yaml
```

## Create ingress

```
kubectl apply -f manifests/ingress.yaml
```
