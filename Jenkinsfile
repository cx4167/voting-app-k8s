pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'denish952'
        BUILD_TAG = "${BUILD_NUMBER}"
        DEV_NAMESPACE = 'voting-app-dev'
        PROD_NAMESPACE = 'voting-app'
        KUBECONFIG = '/var/jenkins_home/.kube/config'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                echo 'Pulling Code from GitHub'
                checkout scm
                sh 'git log -1 --oneline'
            }
        }
        
        stage('Build Vote Image') {
            steps {
                echo 'Building Vote Service'
                sh 'docker build -t ${DOCKER_REGISTRY}/voting-app-vote:${BUILD_TAG} -t ${DOCKER_REGISTRY}/voting-app-vote:latest -f vote/Dockerfile vote/'
            }
        }
        
        stage('Build Worker Image') {
            steps {
                echo 'Building Worker Service'
                sh 'docker build -t ${DOCKER_REGISTRY}/voting-app-worker:${BUILD_TAG} -t ${DOCKER_REGISTRY}/voting-app-worker:latest -f worker/Dockerfile worker/'
            }
        }
        
        stage('Build Result Image') {
            steps {
                echo 'Building Result Service'
                sh 'docker build -t ${DOCKER_REGISTRY}/voting-app-result:${BUILD_TAG} -t ${DOCKER_REGISTRY}/voting-app-result:latest -f result/Dockerfile result/'
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing to Docker Hub'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${DOCKER_REGISTRY}/voting-app-vote:${BUILD_TAG}
                        docker push ${DOCKER_REGISTRY}/voting-app-vote:latest
                        docker push ${DOCKER_REGISTRY}/voting-app-worker:${BUILD_TAG}
                        docker push ${DOCKER_REGISTRY}/voting-app-worker:latest
                        docker push ${DOCKER_REGISTRY}/voting-app-result:${BUILD_TAG}
                        docker push ${DOCKER_REGISTRY}/voting-app-result:latest
                        docker logout
                    '''
                }
            }
        }
        
        stage('Update Manifests') {
            steps {
                echo 'Updating K8s manifests with build tag'
                sh '''
                    sed -i "s|denish952/voting-app-vote:.*|denish952/voting-app-vote:${BUILD_TAG}|g" k8s-yaml/vote-deployment-prod.yaml
                    sed -i "s|denish952/voting-app-worker:.*|denish952/voting-app-worker:${BUILD_TAG}|g" k8s-yaml/worker-deployment.yaml
                    sed -i "s|denish952/voting-app-result:.*|denish952/voting-app-result:${BUILD_TAG}|g" k8s-yaml/result-deployment.yaml
                '''
            }
        }
        
        stage('Deploy to DEV') {
            steps {
                echo 'Deploying to DEV Namespace'
                sh '''
                    # Create namespace
                    kubectl create namespace ${DEV_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                    
                    # Handle StatefulSet (preserve PVC)
                    kubectl delete statefulset db -n ${DEV_NAMESPACE} --cascade=orphan 2>/dev/null || true
                    sleep 5
                    
                    # Apply all manifests
                    kubectl apply -f k8s-yaml/configmap-prod.yaml -n ${DEV_NAMESPACE}
                    kubectl apply -f k8s-yaml/secrets.yaml -n ${DEV_NAMESPACE}
                    kubectl apply -f k8s-yaml/pv-prod.yaml -n ${DEV_NAMESPACE}
                    kubectl apply -f k8s-yaml/db-statefulset-prod.yaml -n ${DEV_NAMESPACE}
                    kubectl apply -f k8s-yaml/redis-deployment.yaml -n ${DEV_NAMESPACE}
                    kubectl apply -f k8s-yaml/vote-deployment-prod.yaml -n ${DEV_NAMESPACE}
                    kubectl apply -f k8s-yaml/result-deployment.yaml -n ${DEV_NAMESPACE}
                    kubectl apply -f k8s-yaml/worker-deployment.yaml -n ${DEV_NAMESPACE}
                    
                    # Wait for deployments to be ready
                    kubectl wait --for=condition=available --timeout=300s deployment -l app=db -n ${DEV_NAMESPACE} 2>/dev/null || true
                    
                    # Display status
                    echo "=== DEV Namespace Resources ==="
                    kubectl get all -n ${DEV_NAMESPACE}
                    echo ""
                    echo "=== Pod Status ==="
                    kubectl get pods -n ${DEV_NAMESPACE}
                '''
            }
        }
        
        stage('Health Check - DEV') {
            steps {
                echo 'Checking DEV deployment health'
                sh '''
                    echo "Waiting for all pods to be ready..."
                    kubectl wait --for=condition=ready pod -l app=vote -n ${DEV_NAMESPACE} --timeout=180s 2>/dev/null || true
                    kubectl wait --for=condition=ready pod -l app=result -n ${DEV_NAMESPACE} --timeout=180s 2>/dev/null || true
                    kubectl wait --for=condition=ready pod -l app=worker -n ${DEV_NAMESPACE} --timeout=180s 2>/dev/null || true
                    
                    echo "DEV deployment health check completed"
                    kubectl get pods -n ${DEV_NAMESPACE}
                '''
            }
        }
        
        stage('Approval') {
            steps {
                input message: 'Deploy to Production?', ok: 'Deploy to PROD'
            }
        }
        
        stage('Deploy to PROD') {
            steps {
                echo 'Deploying to PRODUCTION Namespace'
                sh '''
                    # Create namespace
                    kubectl create namespace ${PROD_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                    
                    # Handle StatefulSet (preserve PVC and data)
                    kubectl delete statefulset db -n ${PROD_NAMESPACE} --cascade=orphan 2>/dev/null || true
                    sleep 5
                    
                    # Apply all manifests
                    kubectl apply -f k8s-yaml/configmap-prod.yaml -n ${PROD_NAMESPACE}
                    kubectl apply -f k8s-yaml/secrets.yaml -n ${PROD_NAMESPACE}
                    kubectl apply -f k8s-yaml/pv-prod.yaml -n ${PROD_NAMESPACE}
                    kubectl apply -f k8s-yaml/db-statefulset-prod.yaml -n ${PROD_NAMESPACE}
                    kubectl apply -f k8s-yaml/redis-deployment.yaml -n ${PROD_NAMESPACE}
                    kubectl apply -f k8s-yaml/vote-deployment-prod.yaml -n ${PROD_NAMESPACE}
                    kubectl apply -f k8s-yaml/result-deployment.yaml -n ${PROD_NAMESPACE}
                    kubectl apply -f k8s-yaml/worker-deployment.yaml -n ${PROD_NAMESPACE}
                    
                    # Wait for deployments to be ready
                    kubectl wait --for=condition=available --timeout=300s deployment -l app=db -n ${PROD_NAMESPACE} 2>/dev/null || true
                    
                    # Display status
                    echo "=== PROD Namespace Resources ==="
                    kubectl get all -n ${PROD_NAMESPACE}
                    echo ""
                    echo "=== Pod Status ==="
                    kubectl get pods -n ${PROD_NAMESPACE}
                '''
            }
        }
        
        stage('Health Check - PROD') {
            steps {
                echo 'Checking PROD deployment health'
                sh '''
                    echo "Waiting for all pods to be ready..."
                    kubectl wait --for=condition=ready pod -l app=vote -n ${PROD_NAMESPACE} --timeout=180s 2>/dev/null || true
                    kubectl wait --for=condition=ready pod -l app=result -n ${PROD_NAMESPACE} --timeout=180s 2>/dev/null || true
                    kubectl wait --for=condition=ready pod -l app=worker -n ${PROD_NAMESPACE} --timeout=180s 2>/dev/null || true
                    
                    echo "PROD deployment health check completed"
                    kubectl get pods -n ${PROD_NAMESPACE}
                '''
            }
        }
        
        stage('Post-Deployment Verification') {
            steps {
                echo 'Verifying deployment'
                sh '''
                    echo "=== Services ==="
                    kubectl get svc -n ${PROD_NAMESPACE}
                    echo ""
                    echo "=== Persistent Volumes ==="
                    kubectl get pv,pvc -n ${PROD_NAMESPACE}
                    echo ""
                    echo "=== Deployment Info ==="
                    kubectl describe deployment vote -n ${PROD_NAMESPACE} | grep -A 5 "Image:"
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up old Docker images'
            sh 'docker image prune -af --filter "until=168h" || true'
        }
        success {
            echo '✅ Pipeline succeeded! Voting app deployed successfully.'
            sh '''
                echo "Access the application:"
                echo "Vote App: kubectl port-forward svc/vote-service 8080:80 -n ${PROD_NAMESPACE}"
                echo "Result App: kubectl port-forward svc/result-service 5000:80 -n ${PROD_NAMESPACE}"
            '''
        }
        failure {
            echo '❌ Pipeline failed! Check logs above.'
        }
        unstable {
            echo '⚠️ Pipeline is unstable. Review the deployment.'
        }
    }
}