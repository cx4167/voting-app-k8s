3 ec2(2 cluster,1 jenkins)



we need to connect k8s clustr to jenkins 
get a .kube/config file from master node
  ```
  cat ~/.kube/config
  ````
copy this and past in 
    ``` vi /var/lib/jenkins/.kube/config
    ```
then give permission
```
sudo chown /var/lib/jenkins/.kube/config
sudo chmod 600 /var/lib/jenkins/.kube/config
```

Download kubectl
```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```
Make it executable
```
chmod +x kubectl
```
move to system path
```
sudo mv kubectl /usr/local/bin/kubectl
```

# Verify installation
kubectl version --client

# Should show: version.Info{...}
