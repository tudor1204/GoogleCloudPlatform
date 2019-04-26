# Hello Application with IAP example

> **Note:** This application is a copy of [hello-app](../hello-app) sample.
> See that directory for more details on this sample.

In this demo, we open two ports on the hello-app container, 8081
and 8082, for two services. For each service, we assign a path, and then 
use Cloud IAP to configure different access for it. To serve HTTPS traffic, we 
will create a Google managed SSL certificate for the endpoint, so make sure you are using a 1.12+
cluster.

## Build the image

```
export PROJ=YOUR_PROJECT
docker build -t gcr.io/${PROJ}/hello-app-iap:v1 -f Dockerfile  .
docker push gcr.io/${PROJ}/hello-app-iap:v1
```

## Deploy the containers

Replace `YOUR_PROJECT` in `deployment.yaml` and apply it.
```
kubectl apply -f manifests/deployment.yaml
```

## Reserve a static IP

We will assign the static IP `iap-test` to the ingress later.
```
gcloud compute addresses create iap-test --global
```

## Create SSL cert

If you have your own domain, create an A record pointing to `iap-test` we just created.
There are many vendors proding free domains. In this demo, we use `iap-test.tk`, as
listed in `domains` field. By creating a ManagedCertificate object, GCP will help 
create the certificate for the SSL traffic.
```
kubectl apply -f manifests/cert.yaml
```

## Create OAuth credentials and add authorized domains

Follow the [offical guide](https://cloud.google.com/iap/docs/enabling-kubernetes-howto#oauth-credentials)
to create the credentials. Cloud IAP protects the domain, so use the your own domain
for the redirect and add it to the authorized domains.


## Create a secret

Download the JSON. Then find the `client_id_key` and
`client_secret_key` from the JSON file.
```
kubectl create secret generic my-secret --from-literal=client_id=client_id_key \
    --from-literal=client_secret=client_secret_key
```

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

## Configure access

Go to Cloud IAP tab, you may find `default/service1` and
`default/service2`, which are both enabled IAP.
Let's only allow account `foo@` has the access of `default/service2`. 
Then if you use this account to access `https://iap-test.tk`, you will
see an error page. But if `https://iap-test.tk/page2/#`, you can see:
```
Hello, world from service2
Full path: deployment-59fb4975f-4lz4h/page2/#
```
