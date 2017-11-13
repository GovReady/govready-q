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
        sh 'apt-get update && apt-get install -y graphviz unzip pandoc wkhtmltopdf jq && apt-get clean'
        sh 'pip install -r requirements.txt'
        sh './fetch-vendor-resources.sh'
      }
    }
  }
}