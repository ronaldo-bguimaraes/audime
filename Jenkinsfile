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
                        rm -f .env
                        cp "$ENV_FILE" .env
                        docker compose build
                    '''
                }
            }
        }

        stage('Migrate') {
            steps {
                withCredentials([file(credentialsId: 'audime_env', variable: 'ENV_FILE')]) {
                    sh 'docker compose run --rm backend alembic upgrade head'
                }
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose up -d'
            }
        }
    }
}
