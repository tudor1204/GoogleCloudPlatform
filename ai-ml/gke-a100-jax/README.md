# JAX 'Hello World' on GKE + A100-80GB

## Goal

This repository contains instructions to create a GKE cluster in Google Cloud 
connected to 4 nodes, each with 8 NVIDIA A100 80G GPUs and run a JAX example as a K8s Job on the GPUs with one process per GPU and 8 processes per node.

### Prerequisites

- A GCP Project with billing setup
- Cloud SDK, docker and kubectl installed in the machine where you are running these steps
- Clone this repo

## Getting Started

### Preparing GKE cluster

- Enable the required APIs

```
   gcloud services enable container.googleapis.com
   gcloud services enable containerregistry.googleapis.com
```

- (If not created with the project) Create default VPC network

```
   gcloud compute networks create default \
    --subnet-mode=auto \
    --bgp-routing-mode=regional \
    --mtu=1460
```

- Create a GKE cluster (for the control plane)

```
   gcloud container clusters create jax-example \
    --zone=us-central1-c
```

- Create a Node Pool where the GPUs will be attached.
This Node Pool will have four `a2-ultragpu-8g` node, each with
8 A100-80Gb GPUs.

> For the purpose of this demo, you will be using a preemptible node,
which has a lower cost, and also does not require GPU quota increase
for your project.

> Detailed steps to [create a GKE cluster with gVNIC](https://cloud.google.com/kubernetes-engine/docs/how-to/using-gvnic)

> General guide to [use GPUs on GKE](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus) 

```
   gcloud container node-pools create gpus-node-pool \
    --machine-type=a2-ultragpu-8g --cluster=jax-example \
    --enable-gvnic --zone=us-central1-c \
    --num-nodes=4 --preemptible
```

- Install NVIDIA drivers on the cluster

```
   kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded-latest.yaml
```

### Packaging JAX code in a container

You can review the JAX code included in `train.py`

- Build the container image and push to the project's container registry

```
   bash build_push_container.sh
```

> The container image is big. These steps might take a few minutes to complete.

### Launch the JAX container 

The yaml files in the `kubernetes` folder have all the configuration needed to run 
the JAX code as a Kubernetes Job.

- Change the image name in the `kubernetes/job.yaml` and `kubernetes/kustomization.yaml` files
> Your image name should be something like `gcr.io/<<PROJECT>>/jax/hello:latest`

- Deploy the components in the GKE cluster you created

```
   cd kubernetes
   kubectl apply -k .
```

- Check that the job has been created

```
   kubectl get jobs
```

You should see somehting similar to this:

```
   NAME              COMPLETIONS   DURATION   AGE
jax-hello-world      0/32          5s         5s
```

- Check the Pods that the job has created

```
   kubectl get pods
```

You should see something simlar to this:
```
NAME                      READY   STATUS        RESTARTS   AGE
jax-hello-world-3-zkhbf   0/1     Pending             0          0s
jax-hello-world-6-rgg7j   0/1     Pending             0          0s
...
```

> Be patient, the GKE cluster needs to pull the container image, and this might take a few minutes the first time

- Once the status of the pods is `Running` or `Terminated`, copy the name of one of the pods and check the logs. 
It contains the output of running the JAX code in `train.py`

```
   kubectl logs jax-hello-world-4-k82vv
```

If verything goes well, you should see an output similar to this

```
$ kubectl logs jax-hello-world-4-k82vv
I0301 20:48:15.699101 139823437018944 distributed.py:59] JAX distributed initialized with visible devices: 0
I0301 20:48:15.700560 139823437018944 distributed.py:79] Connecting to JAX distributed service on 10.68.5.45:1234
I0301 20:48:17.498148 139823437018944 xla_bridge.py:355] Unable to initialize backend 'tpu_driver': NOT_FOUND: Unable to find driver in registry given worker:
I0301 20:48:19.122679 139823437018944 xla_bridge.py:355] Unable to initialize backend 'rocm': NOT_FOUND: Could not find registered platform with name: "rocm". Available platform names are: Interpreter Host CUDA
I0301 20:48:19.123327 139823437018944 xla_bridge.py:355] Unable to initialize backend 'tpu': module 'jaxlib.xla_extension' has no attribute 'get_tpu_client'
I0301 20:48:19.123464 139823437018944 xla_bridge.py:355] Unable to initialize backend 'plugin': xla_extension has no attributes named get_plugin_device_client. Compile TensorFlow with //tensorflow/compiler/xla/python:enable_plugin_device set to true (defaults to false) to enable this.
Coordinator host name: jax-hello-world-0.headless-svc
Coordinator IP address: 10.68.5.45
JAX process 4/32 initialized on jax-hello-world-4
JAX global devices:[StreamExecutorGpuDevice(id=0, process_index=0, slice_index=0), StreamExecutorGpuDevice(id=1, process_index=1, slice_index=1), StreamExecutorGpuDevice(id=2, process_index=2, slice_index=2), StreamExecutorGpuDevice(id=3, process_index=3, slice_index=3), StreamExecutorGpuDevice(id=4, process_index=4, slice_index=1), StreamExecutorGpuDevice(id=5, process_index=5, slice_index=3), StreamExecutorGpuDevice(id=6, process_index=6, slice_index=0), StreamExecutorGpuDevice(id=7, process_index=7, slice_index=2), StreamExecutorGpuDevice(id=8, process_index=8, slice_index=1), StreamExecutorGpuDevice(id=9, process_index=9, slice_index=3), StreamExecutorGpuDevice(id=10, process_index=10, slice_index=0), StreamExecutorGpuDevice(id=11, process_index=11, slice_index=2), StreamExecutorGpuDevice(id=12, process_index=12, slice_index=1), StreamExecutorGpuDevice(id=13, process_index=13, slice_index=3), StreamExecutorGpuDevice(id=14, process_index=14, slice_index=2), StreamExecutorGpuDevice(id=15, process_index=15, slice_index=3), StreamExecutorGpuDevice(id=16, process_index=16, slice_index=1), StreamExecutorGpuDevice(id=17, process_index=17, slice_index=2), StreamExecutorGpuDevice(id=18, process_index=18, slice_index=2), StreamExecutorGpuDevice(id=19, process_index=19, slice_index=1), StreamExecutorGpuDevice(id=20, process_index=20, slice_index=0), StreamExecutorGpuDevice(id=21, process_index=21, slice_index=1), StreamExecutorGpuDevice(id=22, process_index=22, slice_index=3), StreamExecutorGpuDevice(id=23, process_index=23, slice_index=0), StreamExecutorGpuDevice(id=24, process_index=24, slice_index=1), StreamExecutorGpuDevice(id=25, process_index=25, slice_index=0), StreamExecutorGpuDevice(id=26, process_index=26, slice_index=2), StreamExecutorGpuDevice(id=27, process_index=27, slice_index=2), StreamExecutorGpuDevice(id=28, process_index=28, slice_index=3), StreamExecutorGpuDevice(id=29, process_index=29, slice_index=0), StreamExecutorGpuDevice(id=30, process_index=30, slice_index=0), StreamExecutorGpuDevice(id=31, process_index=31, slice_index=3)]
JAX local devices:[StreamExecutorGpuDevice(id=4, process_index=4, slice_index=1)]
[32.]
```

## License

Apache 2.0 - See [LICENSE](LICENSE) for more information.
