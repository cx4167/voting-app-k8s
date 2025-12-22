install prometheus 
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
expose the prometheus server using node port 
```
[root@master ~]# kubectl expose service prometheus-server \
  --type=NodePort \
  --target-port=9090 \
  --name=prometheus-server-ext
service/prometheus-server-ext exposed
```
```
[root@master ~]# kubectl get svc
NAME                            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
kubernetes                      ClusterIP   10.96.0.1        <none>        443/TCP        20d
prometheus-alertmanager         ClusterIP   10.97.199.174    <none>        80/TCP         12m
prometheus-kube-state-metrics   ClusterIP   10.102.39.201    <none>        8080/TCP       12m
prometheus-node-exporter        ClusterIP   10.100.190.144   <none>        9100/TCP       12m
prometheus-pushgateway          ClusterIP   10.105.32.155    <none>        9091/TCP       12m
prometheus-server               ClusterIP   10.110.66.193    <none>        80/TCP         12m
prometheus-server-ext           "NodePort"   10.96.217.69     <none>        80:30921/TCP   52s

```

add grafana repo
```
[root@master ~]# helm repo add grafana https://grafana.github.io/helm-charts
"grafana" has been added to your repositories
```
install grafana 
```
[root@master ~]# helm install grafana grafana/grafana
NAME: grafana
LAST DEPLOYED: Mon Dec 22 06:47:01 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
1. Get your 'admin' user password by running:

   kubectl get secret --namespace default grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo


2. The Grafana server can be accessed via port 80 on the following DNS name from within your cluster:

   grafana.default.svc.cluster.local

   Get the Grafana URL to visit by running these commands in the same shell:
     export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=grafana" -o jsonpath="{.items[0].metadata.name}")
     kubectl --namespace default port-forward $POD_NAME 3000

3. Login with the password from step 1 and the username: admin
#################################################################################
######   WARNING: Persistence is disabled!!! You will lose your data when   #####
######            the Grafana pod is terminated.                            #####
#################################################################################
[root@master ~]#
```
```
 [root@master ~]# kubectl get svc -n default grafana
NAME      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
grafana   ClusterIP   10.104.172.23   <none>        80/TCP    4m19s
[root@master ~]#
```
expose the grafana using node port 
```
get-port=3000 \
  --name=grafana-ext
service/grafana-ext exposed
```
```
[root@master ~]# kubectl get svc grafana-ext
NAME          TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
grafana-ext   NodePort   10.104.64.184   <none>        80:30361/TCP   63s
```
get password to login 
```
kubectl get secret --namespace default grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

[root@master ~]# kubectl get secret --namespace default grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
P4UfWM3ASP2WH1LJZralJAUns4QFW16kD3PMBut3
```
also expose prometheus-kube-state-metrics
```
[root@master ~]# kubectl expose service prometheus-kube-state-metrics --type=NodePort --target-port=8080 --name=prometheus-kube-state-metrics-ext
service/prometheus-kube-state-metrics-ext exposed
[root@master ~]# kubectl get svc
NAME                                TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
grafana                             ClusterIP   10.104.172.23    <none>        80/TCP           28m
grafana-ext                         NodePort    10.104.64.184    <none>        80:30361/TCP     19m
kubernetes                          ClusterIP   10.96.0.1        <none>        443/TCP          20d
prometheus-alertmanager             ClusterIP   10.97.199.174    <none>        80/TCP           50m
prometheus-kube-state-metrics       ClusterIP   10.102.39.201    <none>        8080/TCP         50m
prometheus-kube-state-metrics-ext   NodePort    10.106.237.129   <none>        8080:32647/TCP   20s
prometheus-node-exporter            ClusterIP   10.100.190.144   <none>        9100/TCP         50m
prometheus-pushgateway              ClusterIP   10.105.32.155    <none>        9091/TCP         50m
prometheus-server                   ClusterIP   10.110.66.193    <none>        80/TCP           50m
prometheus-server-ext               NodePort    10.96.217.69     <none>        80:30921/TCP     38m
[root@master ~]#
```


to see inside pometheus 
 ```
[root@master ~]# kubectl get cm
NAME                      DATA   AGE
grafana                   1      34m
kube-root-ca.crt          1      20d
prometheus-alertmanager   2      57m
prometheus-server         6      57m
[root@master ~]#
[root@master ~]# kubectl edit cm prometheus-server

# Please edit the object below. Lines beginning with a '#' will be ignored,
# and an empty file will abort the edit. If an error occurs while saving this file will be
# reopened with the relevant failures.
#
apiVersion: v1
data:
  alerting_rules.yml: |
    {}
  alerts: |
    {}
  allow-snippet-annotations: "false"
  prometheus.yml: |
    global:
      evaluation_interval: 1m
      scrape_interval: 1m
      scrape_timeout: 10s
    rule_files:
    - /etc/config/recording_rules.yml
    - /etc/config/alerting_rules.yml
    - /etc/config/rules
    - /etc/config/alerts
    scrape_configs:
    - job_name: prometheus
      static_configs:
      - targets:
        - localhost:9090
    - bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      job_name: kubernetes-apiservers
      kubernetes_sd_configs:
      - role: endpoints
      relabel_configs:
      - action: keep
        regex: default;kubernetes;https
        source_labels:

```


