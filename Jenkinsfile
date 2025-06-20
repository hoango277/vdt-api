
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
        TAG_REF = ""
        TAG_NAME = ""
        DOCKER_IMAGE = "xuanhoa2772004/vdt-api:${TAG_NAME}"
    }
    stages {
        stage('Checkout Source Repo') {
            steps {
                dir('source') {
                    git branch: "${GIT_BRANCH}", credentialsId: "${GIT_CRED}", url: "${GIT_SOURCE_REPO}"
                }
            }
        }
        stage('Check Tag On Commit') {
            steps {
                script {
                    // Fetch tag mới nhất về local (nên làm sau khi checkout)
                    sh 'git fetch --tags'

                    // Kiểm tra commit hiện tại có đúng là một tag không
                    def tagName = sh(
                        script: 'git describe --tags --exact-match || true',
                        returnStdout: true
                    ).trim()

                    if (tagName) {
                        echo "Commit hiện tại là một tag: ${tagName} => tiếp tục build."
                        env.TAG_NAME = tagName
                    } else {
                        echo "Commit hiện tại KHÔNG phải là một tag. Abort pipeline."
                        currentBuild.result = 'ABORTED'
                        error("Commit này không được gắn tag, không build!")
                    }
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