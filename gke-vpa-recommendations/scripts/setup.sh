
echo "Configuring region and zone"
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

echo "Creating a gke cluster"
gcloud container clusters create online-boutique \
    --project=${PROJECT_ID} --zone=${ZONE} 


sleep 7 &
PID=$!
i=1
sp="/-\|"
echo -n ' '
while [ -d /proc/$PID ]
do
  printf "\b${sp:i++%${#sp}:1}"
done

echo "Get credentials for your cluster"
gcloud container clusters get-credentials online-boutique


echo "deploy the onlineshop"
kubectl apply -f k8s/online-shop.yaml


echo "SETUP COMPLETE"
