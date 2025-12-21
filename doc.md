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
```
kubectl version --client
```

#jenkins container 
```
FROM jenkins/jenkins:lts

USER root

# Install Docker CLI (static)
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-26.1.3.tgz -o docker.tgz \
 && tar -xzf docker.tgz \
 && mv docker/docker /usr/local/bin/docker \
 && chmod +x /usr/local/bin/docker \
 && rm -rf docker docker.tgz

# Install kubectl (fetch stable release then download)
RUN set -eux; \
    KUBECTL_VERSION="$(curl -fsSL https://dl.k8s.io/release/stable.txt)"; \
    curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl; \
    chmod +x /usr/local/bin/kubectl

# Install Helm
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

USER jenkins
```

```
services:
  jenkins:
    build: .
    image: jenkins-ci-cd
    container_name: jenkins
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - /opt/jenkins:/var/jenkins_home
      - /opt/jenkins/.kube:/var/jenkins_home/.kube
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - "JAVA_OPTS=-Xmx512m -Xms256m"
      - KUBECONFIG=/var/jenkins_home/.kube/config
    restart: unless-stopped
    user: root
```
