pipeline {
  agent {
    dockerfile {
      filename 'Dockerfile'
    }
    
  }
  stages {
    stage('Build') {
      steps {
        sh 'pip install requirements.txt'
        sh 'fetch-vendor-resources.sh'
      }
    }
  }
}