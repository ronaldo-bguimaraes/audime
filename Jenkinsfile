pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    stages {
        stage('Build') {
            steps {
                withCredentials([file(credentialsId: 'audime_env', variable: 'ENV_FILE')]) {
                    sh '''
                        sudo cp "$ENV_FILE" .env
                        sudo docker compose build backend
                    '''
                }
            }
        }

        stage('Migrate') {
            steps {
                withCredentials([file(credentialsId: 'audime_env', variable: 'ENV_FILE')]) {
                    sh 'sudo docker compose run --rm backend alembic upgrade head'
                }
            }
        }

        stage('Deploy') {
            steps {
                sh 'sudo docker compose up -d'
            }
        }
    }
}