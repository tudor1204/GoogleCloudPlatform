DATASETS_DIR="datasets"
QUEUE_NAME="datasets"
POD_NAME="redis-leader"
PVC_PATH="/mnt/fileserver"

echo "Copying datasets to pod '${POD_NAME}'..."
kubectl cp ${DATASETS_DIR} ${POD_NAME}:${PVC_PATH}
