#!/usr/bin/env bash
DATASETS_DIR="datasets"
QUEUE_NAME="datasets"
POD_NAME="redis-leader"
PVC_PATH="/mnt/fileserver"

echo "**************************************"
echo "Populating queue for batch training..."
echo "**************************************"
echo "The following datasets will be queued for processing:"
filenames=""
for filepath in ${DATASETS_DIR}/training/*.pkl; do
  echo $filepath
  filenames+=" $filepath"
done

QUEUE_LENGTH=$(kubectl exec ${POD_NAME} -- /bin/sh -c \
  "redis-cli rpush ${QUEUE_NAME} ${filenames}")

echo "Queue length: ${QUEUE_LENGTH}"
