# deploys app locally in minikube environment

#!/bin/bash
  echo "Deploying Dicto to Kubernetes..."
  eval $(minikube docker-env)
  docker build -t dicto:latest .
  kubectl apply -f k8s/secret.yaml
  kubectl apply -f k8s/deployment-local.yaml
  kubectl apply -f k8s/service.yaml
  echo "Deployment complete!"
  echo "Starting port-forward on http://localhost:9000..."
  kubectl port-forward service/dicto-service 9000:80
