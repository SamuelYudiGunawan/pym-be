#!/bin/bash
# Undeploy Pour Your Mind from Oracle Cloud OKE

echo "This will delete all Pour Your Mind resources from your cluster."
read -p "Are you sure? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo "Deleting namespace (this will remove all resources)..."
kubectl delete namespace pour-your-mind

echo ""
echo "Done! All resources have been removed."
echo ""
echo "Note: OCI Load Balancers may take a few minutes to be fully terminated."
