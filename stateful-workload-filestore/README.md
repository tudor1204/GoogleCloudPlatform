# Stateful workload with Filestore tutorial

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/GoogleCloudPlatform/kubernetes-engine-samples&cloudshell_tutorial=README.md&cloudshell_workspace=guestbook/)

## Design

This tutorial will create writer Deployments that write to the NFS (Filestore), and create reader Deployments that will read from the same file in NFS. The user can then access the reader externally to see the changes the writer made to the file. 
Technologies used in this tutorial
- Google Kubernetes Engine (GKE)
- Google Filestore (used as NFS)

## Multiple/concurrent access to persistent data

- This tutorial will use NFS (Google Filestore) as a way to showcase scalable stateful workloads and allow ReadWriteMany access mode for PV and PVC
- The writer is a Deployment workload
    - Each pod has access to write to the NFS that is mounted
    - Each pod will write the current time and name of the pod to a shared file with other writers and readers
    - The writer has a script that will write to this file every 30 seconds indefinitely (time interval configurable)
    - Showcase ReadWriteMany by having > 2 pods writing at the same time
- The reader workload is a Deployment, that exposes it externally via Load Balancer
    - The reader can at a glance, see the history of writers that are actively writing to the file
    - The reader only has read access

## Scalability
- The reader/writer Deployments can be easily scaled up or down, while maintaining connection to the shared FileStore NFS with ReadWriteMany access
- Start with 2 writer pods, then scale up to 5 pods to showcase scalability with NFS
The user will be able to see 5 different writers all writing to the same file

Please follow the tutorial at https://cloud.google.com/kubernetes-engine/docs/tutorials/stateful-workload
