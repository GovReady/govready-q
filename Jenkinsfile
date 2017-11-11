pipeline {
  agent {
    docker {
      image 'python:3'
      args '-p 8000:8000'
    }
    
  }
  stages {
    stage('Build') {
      steps {
        sh 'pip install -r requirements.txt'
        sh './fetch-vendor-resources.sh'
      }
    }
  }
}