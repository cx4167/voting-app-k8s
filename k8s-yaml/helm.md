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

