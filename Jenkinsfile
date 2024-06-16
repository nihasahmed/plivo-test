pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'plivotestrepo.azurecr.io'
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/your-image-name"
        AZURE_CREDENTIALS = 'azure-sp'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from the specified Git repository
                git branch: 'main', url: 'https://github.com/nihasahmed/plivo-test.git'
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
                sh 'python -m venv venv'
                sh './venv/bin/pip install -r requirements.txt'
                // Run unit tests
                sh './venv/bin/pytest'
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
                    docker.withRegistry("https://${DOCKER_REGISTRY}", AZURE_CREDENTIALS) {
                        // Push the image with the build ID tag
                        dockerImage.push()
                        // Push the same image with the 'latest' tag
                        dockerImage.push('latest')
                    }
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
