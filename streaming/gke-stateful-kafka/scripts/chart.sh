#!/bin/bash

# Dependency name and new version as arguments
DEPENDENCY_NAME=$1
NEW_VERSION=$2

# Update the version in Chart.yaml using sed
# This sed command is designed to match the specific structure of your Chart.yaml
sed -i "/- name: $DEPENDENCY_NAME/,/version: /s/version: .*/version: $NEW_VERSION/" Chart.yaml
