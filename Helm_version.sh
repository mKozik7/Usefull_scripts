#!/bin/bash

subscriptions=$(az account list  -o tsv --query "[].id")

for sub in $subscriptions; do
    echo "Cluster in subscription: $sub" 
    az account set --subscription $sub
    cluster=$(az aks list -o tsv --query "[].name") 
    resourceGroup=$(az aks list -o tsv --query "[].resourceGroup" | sort | uniq) 
    for cluster in $cluster; do
        az aks get-credentials --name $cluster --resource-group $resourceGroup
        kubelogin convert-kubeconfig -l azurecli
        # echo $cluster >> info.txt
        # echo $resourceGroup >> info.txt
        helm list -n datadog >> info.txt
    done
done 