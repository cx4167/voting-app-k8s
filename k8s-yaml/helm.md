#download helm
```
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```
output 
Downloading https://get.helm.sh/helm-v3.19.4-linux-amd64.tar.gz
Verifying checksum... Done.
Preparing to install helm into /usr/local/bin
helm installed into /usr/local/bin/helm
#add promethesis repo 
```
 helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
```
output 
--------"prometheus-community" has been added to your repositories

#update the repo 
```
helm reop update
```

#install helm 
```
helm install prometheus prometheus-community/prometheus \
  --version 15.18.0
```
output 
```
NAME: prometheus
LAST DEPLOYED: Mon Dec 22 06:24:52 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
The Prometheus server can be accessed via port 80 on the following DNS name from within your cluster:
prometheus-server.default.svc.cluster.local


Get the Prometheus server URL by running these commands in the same shell:
  export POD_NAME=$(kubectl get pods --namespace default -l "app=prometheus,component=server" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace default port-forward $POD_NAME 9090


The Prometheus alertmanager can be accessed via port 80 on the following DNS name from within your cluster:
prometheus-alertmanager.default.svc.cluster.local


Get the Alertmanager URL by running these commands in the same shell:
  export POD_NAME=$(kubectl get pods --namespace default -l "app=prometheus,component=alertmanager" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace default port-forward $POD_NAME 9093
#################################################################################
######   WARNING: Pod Security Policy has been moved to a global property.  #####
######            use .Values.podSecurityPolicy.enabled with pod-based      #####
######            annotations                                               #####
######            (e.g. .Values.nodeExporter.podSecurityPolicy.annotations) #####
#################################################################################


The Prometheus PushGateway can be accessed via port 9091 on the following DNS name from within your cluster:
prometheus-pushgateway.default.svc.cluster.local


Get the PushGateway URL by running these commands in the same shell:
  export POD_NAME=$(kubectl get pods --namespace default -l "app=prometheus,component=pushgateway" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace default port-forward $POD_NAME 9091

For more information on running Prometheus, visit:
https://prometheus.io/
```
```
[root@master ~]# kubectl get pods
NAME                                             READY   STATUS    RESTARTS   AGE
prometheus-alertmanager-7dd9fdc769-6wcfp         2/2     Running   0          2m42s
prometheus-kube-state-metrics-585fcf7bd5-8rbs5   1/1     Running   0          2m42s
prometheus-node-exporter-k6mgb                   1/1     Running   0          2m42s
prometheus-pushgateway-85f5b4b4c6-hzsmg          1/1     Running   0          2m42s
prometheus-server-c4f46566b-2h966                2/2     Running   0          2m42s
[root@master ~]#
```
