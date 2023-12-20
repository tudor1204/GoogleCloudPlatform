# Update Helm Chart.yaml dependency and version

# Usage update the Helm Chart kafka version 20.0.6

# scripts/chart.sh kafka 20.0.6 
#!/bin/bash

# Dependency name and new version as arguments
DEPENDENCY_NAME=$1
NEW_VERSION=$2

# Update the version in Chart.yaml using sed
# This sed command is designed to match the specific structure of your Chart.yaml
sed -i "/- name: $DEPENDENCY_NAME/,/version: /s/version: .*/version: $NEW_VERSION/" Chart.yaml
