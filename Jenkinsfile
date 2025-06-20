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
        DOCKER_IMAGE = "" // Sẽ gán sau khi lấy được tag
        TAG_NAME = ""     // Sẽ gán sau khi fetch tag
    }
    stages {
        stage('Check Tag Release & Fetch Tags') {
            steps {
                dir('source') {
                    script {
                        // Lấy ref từ biến môi trường Jenkins
                        env.TAG_REF = env.GIT_BRANCH ?: env.BRANCH_NAME ?: env.TAG_NAME ?: ''
                        echo "TAG_REF: ${env.TAG_REF}"
                        if (!env.TAG_REF.startsWith('refs/tags/')) {
                            echo "Not a tag release. Stopping pipeline."
                            currentBuild.result = 'ABORTED'
                            error("Pipeline runs only on tag release!")
                        }
                        // Clone repo, clone branch nào cũng được, chỉ cần fetch tag sau đó
                        git branch: "${env.GIT_BRANCH}", credentialsId: "${env.GIT_CRED}", url: "${env.GIT_SOURCE_REPO}"
                        // Fetch toàn bộ tags về local
                        sh 'git fetch --tags'
                        // Gán tag name đúng cho pipeline (cắt tên tag từ ref)
                        env.TAG_NAME = env.TAG_REF.replace('refs/tags/', '')
                        // Gán tên image
                        env.DOCKER_IMAGE = "xuanhoa2772004/vdt-api:${env.TAG_NAME}"

                        echo "TAG_NAME: ${env.TAG_NAME}"
                        echo "DOCKER_IMAGE: ${env.DOCKER_IMAGE}"

                        // Kiểm tra tag đã tồn tại trên remote chưa (tránh build lại tag cũ)
                        def tagExists = sh(
                            script: "git ls-remote --tags ${env.GIT_SOURCE_REPO} ${env.TAG_NAME}",
                            returnStdout: true
                        ).trim()
                        if (tagExists) {
                            echo "Tag ${env.TAG_NAME} đã tồn tại trên remote. Dừng pipeline!"
                            currentBuild.result = 'ABORTED'
                            error("Tag đã tồn tại, không build lại!")
                        }
                    }
                }
            }
        }
        stage('Checkout To Tag') {
            steps {
                dir('source') {
                    sh "git checkout ${env.TAG_NAME}"
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
                        echo '==> Build & push image with tag: ${env.TAG_NAME}'
                        /kaniko/executor --dockerfile=Dockerfile --context=. --destination=${env.DOCKER_IMAGE} --verbosity=debug
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
                    sed -i 's|^  tag:.*|  tag: "${env.TAG_NAME}"|' ${env.VALUES_FILE}
                    """
                    sh "cat ${env.VALUES_FILE}"
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
            echo "Pipeline aborted (not a tag release hoặc tag đã tồn tại)."
        }
        success {
            echo "CI/CD completed successfully!"
        }
    }
}
