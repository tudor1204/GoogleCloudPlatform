# use the specified base image / please replace the image with the required one
FROM us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20240220_0936_RC01 as base_image

# declare a new build argument
ARG MODEL_NAME

# set the model name as an environment variable
ENV MODEL_NAME=${MODEL_NAME}

# copy model files from the first stage build
COPY ./$MODEL_NAME /app/$MODEL_NAME
