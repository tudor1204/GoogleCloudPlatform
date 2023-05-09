# -*- coding: utf-8 -*-
"""Pub/Sub pull example on Google Kubernetes Engine.

This program pulls messages from a Cloud Pub/Sub topic and
prints to standard output.
"""

import datetime
import time

from google.cloud import pubsub_v1

PUBSUB_TOPIC = 'echo'
PUBSUB_SUBSCRIPTION = 'echo-read'
# [START gke_pubsub_pull]
# [START container_pubsub_pull]
def main():
    """Continuously pull messages from subsciption"""
    client = pubsub_v1.SubscriberClient()
    request = pubsub_v1.Subscription(
        name=PUBSUB_SUBSCRIPTION,
        topic=PUBSUB_TOPIC,
    )
    subscription = client.create_subscription(request=request)

    print('Pulling messages from Pub/Sub subscription...')
    while True:
        request = pubsub_v1.PullRequest(
            subscription=subscription,
            max_messages=10,
        )
        ack = client.pull(request=request)
        for _, message in list(ack.received_messages):
            print("[{0}] Received message: ID={1} Data={2}".format(
                datetime.datetime.now(),
                message.ack_id,
                message.message))
            process(message)


def process(message):
    """Process received message"""
    print("[{0}] Processing: {1}".format(datetime.datetime.now(),
                                         message.ack_id))
    time.sleep(3)
    print("[{0}] Processed: {1}".format(datetime.datetime.now(),
                                        message.ack_id))
# [END container_pubsub_pull]
# [END gke_pubsub_pull]

if __name__ == '__main__':
    main()
