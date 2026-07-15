pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    stages {
        stage('Deploy') {
            steps {
                dir('/opt/apps/audime') {
                    sh '''
                        git fetch origin
                        git reset --hard origin/main
                        docker compose up -d --build
                    '''
                }
            }
        }
    }
}