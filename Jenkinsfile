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
        TAG_NAME = ""
        DOCKER_IMAGE = ""
    }
    stages {
        stage('Checkout Source Repo') {
            steps {
                dir('source') {
                    git branch: "${env.GIT_BRANCH}", credentialsId: "${env.GIT_CRED}", url: "${env.GIT_SOURCE_REPO}"
                }
            }
        }
        stage('Check Tag On Commit') {
            steps {
                dir('source') {
                    script {
                        sh 'git fetch --tags'
                        def tagName = sh(
                            script: 'git describe --tags --exact-match || true',
                            returnStdout: true
                        ).trim()
                        if (tagName) {
                            echo "Commit hiện tại là một tag: ${tagName} => tiếp tục build."
                            env.TAG_NAME = tagName
                            env.DOCKER_IMAGE = "xuanhoa2772004/vdt-api:${tagName}"
                        } else {
                            echo "Commit hiện tại KHÔNG phải là một tag. Abort pipeline."
                            currentBuild.result = 'ABORTED'
                            error("Commit này không được gắn tag, không build!")
                        }
                    }
                }
            }
        }
        stage('Build & Push Docker Image') {
            steps {
                dir('source') {
                    container('kaniko') {
                        sh """
                        export TAG_NAME="${env.TAG_NAME}"
                        export DOCKER_IMAGE="${env.DOCKER_IMAGE}"
                        echo "==> TAG_NAME = \$TAG_NAME"
                        echo "==> DOCKER_IMAGE = \$DOCKER_IMAGE"
                        echo '==> Checking Kaniko Docker config:'
                        ls -la /kaniko/.docker/
                        cat /kaniko/.docker/config.json || echo "No config.json found"
                        echo '==> Build & push image with tag: \$TAG_NAME'
                        /kaniko/executor --dockerfile=Dockerfile --context=. --destination=\$DOCKER_IMAGE --verbosity=debug
                        """
                    }
                }
            }
        }
        stage('Checkout Config Repo') {
            steps {
                dir('config') {
                    git branch: "${env.GIT_BRANCH}", credentialsId: "${env.GIT_CRED}", url: "${env.GIT_CONFIG_REPO}"
                }
            }
        }
        stage('Update values.yaml') {
            steps {
                dir('config') {
                    sh """
                    export TAG_NAME="${env.TAG_NAME}"
                    export VALUES_FILE="${env.VALUES_FILE}"
                    sed -i 's|^  tag:.*|  tag: "\$TAG_NAME"|' \$VALUES_FILE
                    cat \$VALUES_FILE
                    """
                }
            }
        }
        stage('Commit & Push to Config Repo') {
            steps {
                dir('config') {
                    withCredentials([usernamePassword(credentialsId: "${env.GIT_CRED}", usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                        sh """
                        git config user.email "ci-bot@yourdomain.com"
                        git config user.name "ci-bot"
                        git add ${env.VALUES_FILE}
                        git commit -m "Update image tag to ${env.TAG_NAME} [ci skip]" || echo "No changes to commit"
                        git push https://${GIT_USER}:${GIT_TOKEN}@github.com/hoango277/vdt-config-api.git HEAD:${env.GIT_BRANCH}
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
