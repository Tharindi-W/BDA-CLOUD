#!/bin/bash

# Initialize Minikube cluster using Docker as the driver
echo "Starting Minikube..."
minikube start --driver=docker

# Configure local Docker client to use Minikube's Docker daemon instead of local daemon
# This ensures images are built inside Minikube's environment
echo "Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)

# Build the application Docker image and tag it as hello-world:latest
# Uses the Dockerfile in docker/ directory
echo "Building Docker image..."
docker build -t hello-world:latest -f docker/Dockerfile .

# Apply the ConfigMap that contains application configuration
# This creates/updates the config-map.yaml with environment variables
echo "Applying ConfigMap..."
kubectl apply -f config/config-map.yaml

# Deploy the application components to Kubernetes cluster
# Deployment: Manages the pods running our application containers (scaling, updates, restarts)
# Service: Provides stable networking and load balancing for accessing the pods
echo "Updating Deployment and Service..."
kubectl apply -f manifests/deployment.yaml  # Creates/updates pods running our application
kubectl apply -f manifests/service.yaml     # Creates/updates the load balancer to access pods

# Wait for the application pods to be ready before proceeding
# Timeout after 60 seconds if pods aren't ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=hello-world --timeout=60s

# Display the status of all pods in the cluster
echo "Checking pod status..."
kubectl get pods

# Get logs from the first pod of our application
# First gets the pod name, then retrieves its logs
echo "Checking pod logs..."
POD_NAME=$(kubectl get pods -l app=hello-world -o jsonpath="{.items[0].metadata.name}")
kubectl logs $POD_NAME

# Save Minikube cluster logs to a file for debugging purposes
echo "Saving Minikube logs..."
minikube logs --file=logs.txt

# Print the URL where the application can be accessed
# Uses Minikube's service command to get the external URL
echo "All done! Access your application with:"
minikube service hello-world-service --url

