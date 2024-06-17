pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'plivotestrepo.azurecr.io'
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/message-service"
        AZURE_CREDENTIALS = 'azure-sp'
        KUBECONFIG_CREDENTIALS_ID = 'plivo'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check for Relevant Changes') {
            steps {
                script {
                    def changes = sh(script: 'git diff --name-only HEAD~1 HEAD', returnStdout: true).trim()
                    def irrelevantChanges = changes.split('\n').every { it.startsWith('terraform/') || it.startsWith('k8s/') || it == 'README.md' }
                
                    if (irrelevantChanges) {
                        currentBuild.result = 'SUCCESS'
                        error("Changes only in tf/, k8s/ directories, or README.md file. Skipping build.")
                    }
                }
            }
        }

        stage('Test') {
            when {
                not {
                    equals expected: 'SUCCESS', actual: currentBuild.result
                }
            }
            steps {
                // Set up a virtual environment and install dependencies
                sh 'python3 -m venv venv'
                sh './venv/bin/pip install -r requirements-pytest.txt'
                // Run unit tests
                sh 'export SQLALCHEMY_DATABASE_URI="sqlite:///:memory:" && ./venv/bin/python3 -m pytest'
            }
        }

        stage('Build Docker Image') {
            when {
                not {
                    equals expected: 'SUCCESS', actual: currentBuild.result
                }
            }
            steps {
                script {
                    // Build the Docker image with a tag based on the build ID
                    dockerImage = docker.build("${DOCKER_IMAGE}:${env.BUILD_ID}")
                }
            }
        }

        stage('Push Docker Image') {
            when {
                not {
                    equals expected: 'SUCCESS', actual: currentBuild.result
                }
            }
            steps {
                script {
                    // Log in to the Docker registry using the Azure credentials
                    withCredentials([usernamePassword(credentialsId: AZURE_CREDENTIALS, usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                      sh 'docker login -u $USERNAME -p $PASSWORD https://${DOCKER_REGISTRY}'
                      dockerImage.push()
                      dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                not {
                    equals expected: 'SUCCESS', actual: currentBuild.result
                }
            }
            steps {
                withKubeConfig([credentialsId: KUBECONFIG_CREDENTIALS_ID]) {
                    sh """
                    kubectl set image deployment/message-service message-servicee=${DOCKER_IMAGE}:v${env.BUILD_ID}
                    kubectl rollout status deployment/message-service
                    """
                }
            }
        }
    }

    post {
        always {
            // Clean up the workspace
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
