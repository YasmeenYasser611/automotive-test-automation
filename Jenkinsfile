pipeline {
    agent any

    environment {
        TEST_DIR = 'tests'
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    venv/bin/python -m pip install --upgrade pip
                    venv/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    venv/bin/python -m robot --outputdir ${TEST_DIR}/results ${TEST_DIR}/
                '''
            }
        }
    }

    post {
        always {
            robot outputPath: "${TEST_DIR}/results"
            archiveArtifacts artifacts: "${TEST_DIR}/results/*", allowEmptyArchive: true
        }
    }
}