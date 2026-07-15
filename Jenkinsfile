pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    stages {
        stage('Deploy') {
            steps {
                withCredentials([file(credentialsId: 'audime_env', variable: 'ENV_FILE')]) {
                    sh '''
                        cp "$ENV_FILE" .env
                        docker compose up -d --build
                    '''
                }
            }
        }
    }
}