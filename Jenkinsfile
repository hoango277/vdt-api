pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command:
    - /busybox/cat
    tty: true
    volumeMounts:
      - name: kaniko-secret
        mountPath: /kaniko/.docker
        readOnly: true
  volumes:
    - name: kaniko-secret
      secret:
        secretName: dockerhub-secret
        items:
          - key: .dockerconfigjson
            path: config.json
"""
        }
    }
    environment {
        GIT_SOURCE_REPO = "https://github.com/hoango277/vdt-api.git"
        GIT_CONFIG_REPO = "https://github.com/hoango277/vdt-config-api.git"
        GIT_BRANCH = "main"
        GIT_CRED = "d69c1811-345b-49d4-ac3b-93211abfff77"
        VALUES_FILE = "values.yaml"
        // Nếu Jenkins nhận tag, sẽ có TAG_NAME, nếu không thì rỗng
        TAG_REF = "${env.GIT_BRANCH ?: env.BRANCH_NAME ?: env.TAG_NAME ?: ''}"
        TAG_NAME = "${sh(script: 'echo ${TAG_REF##*/}', returnStdout: true).trim()}"
        DOCKER_IMAGE = "xuanhoa2772004/vdt-api:${TAG_NAME}"
    }
    stages {
        stage('Check Tag Release') {
            steps {
                script {
                    // Kiểm tra webhook có phải là tag release không
                    if (!env.TAG_REF.startsWith('refs/tags/')) {
                        echo "Not a tag release. Stopping pipeline."
                        currentBuild.result = 'ABORTED'
                        // Stop the pipeline
                        error("Pipeline runs only on tag release!")
                    }
                    echo "Triggered by tag: ${TAG_NAME}"
                }
            }
        }
        stage('Checkout Source Repo') {
            steps {
                dir('source') {
                    git branch: "${GIT_BRANCH}", credentialsId: "${GIT_CRED}", url: "${GIT_SOURCE_REPO}"
                    sh "git checkout ${TAG_NAME}"
                }
            }
        }
        stage('Build & Push Docker Image') {
            steps {
                dir('source') {
                    container('kaniko') {
                        sh """
                        echo '==> Checking Kaniko Docker config:'
                        ls -la /kaniko/.docker/
                        cat /kaniko/.docker/config.json || echo "No config.json found"
                        echo '==> Build & push image with tag: ${TAG_NAME}'
                        /kaniko/executor --dockerfile=Dockerfile --context=. --destination=${DOCKER_IMAGE} --verbosity=debug
                        """
                    }
                }
            }
        }
        stage('Checkout Config Repo') {
            steps {
                dir('config') {
                    git branch: "${GIT_BRANCH}", credentialsId: "${GIT_CRED}", url: "${GIT_CONFIG_REPO}"
                }
            }
        }
        stage('Update values.yaml') {
            steps {
                dir('config') {
                    sh """
                    sed -i 's|^  tag:.*|  tag: "${TAG_NAME}"|' ${VALUES_FILE}
                    """
                    sh "cat ${VALUES_FILE}"
                }
            }
        }
        stage('Commit & Push to Config Repo') {
            steps {
                dir('config') {
                    withCredentials([usernamePassword(credentialsId: "${GIT_CRED}", usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                        sh """
                        git config user.email "ci-bot@yourdomain.com"
                        git config user.name "ci-bot"
                        git add ${VALUES_FILE}
                        git commit -m "Update image tag to ${TAG_NAME} [ci skip]" || echo "No changes to commit"
                        git push https://${GIT_USER}:${GIT_TOKEN}@github.com/hoango277/vdt-config-api.git HEAD:${GIT_BRANCH}
                        """
                    }
                }
            }
        }
    }
    post {
        failure {
            echo "Pipeline failed. Please check the logs for more information."
        }
        aborted {
            echo "Pipeline aborted (not a tag release)."
        }
        success {
            echo "CI/CD completed successfully!"
        }
    }
}