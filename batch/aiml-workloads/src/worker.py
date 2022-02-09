#!/usr/bin/env python

import os
import rediswq
from model_training import FraudDetectionModelTrainer

FILESTORE_PATH = "/mnt/fileserver/"
TESTING_DATASET_PATH = FILESTORE_PATH + "datasets/testing/test_dataset.pkl"
OUTPUT_DIR = FILESTORE_PATH + "output/"
REPORT_PATH = OUTPUT_DIR + "report.txt"
CLASS_LABEL = "TX_FRAUD_SCENARIO"
QUEUE_NAME = "datasets"
HOST = "redis"
# Uncomment next two lines if you do not have Kube-DNS working.
# import os
# HOST = os.getenv("REDIS_SERVICE_HOST")

for file in os.listdir(FILESTORE_PATH):
    print(os.path.join(FILESTORE_PATH, file))


def main():
    q = rediswq.RedisWQ(name="datasets", host=HOST)
    print("Worker with sessionID: " + q.sessionID())
    print("Initial queue state: empty=" + str(q.empty()))
    checkpoint_path = None
    while not q.empty():
        item = q.lease(lease_secs=20, block=True, timeout=2)
        if item is not None:
            dataset_path = item.decode("utf-8")
            print("Processing dataset: " + dataset_path)
            training_dataset_path = FILESTORE_PATH + dataset_path
            model_trainer = FraudDetectionModelTrainer(
                training_dataset_path,
                TESTING_DATASET_PATH,
                CLASS_LABEL,
                checkpoint_path=checkpoint_path,
            )
            checkpoint_path = model_trainer.train_and_save(OUTPUT_DIR)
            model_trainer.generate_report(REPORT_PATH)
            q.complete(item)
        else:
            print("Waiting for work")
    print("Queue empty, exiting")


main()
