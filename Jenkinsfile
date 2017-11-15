pipeline {
  agent {
    docker {
      image 'python:3'
      args '-p 8000:8000'
    }
  }
  stages {
    stage('OS Setup') {
      steps {
        sh 'apt-get update && apt-get install -y graphviz unzip pandoc wkhtmltopdf jq locales && apt-get clean'
        sh 'sed -i "s/^[# ]*en_US.UTF-8/en_US.UTF-8/" /etc/locale.gen'
        sh '/usr/sbin/locale-gen'
      }
    }
    stage('Build App') {
      steps {
        sh 'pip install -r requirements.txt'
        sh './fetch-vendor-resources.sh'
      }
    }
    stage('Test App') {
      steps {
        // Leaving out siteapp tests for now, because selenium/chromium isn't working.  See govready-q/issues/334

        withCredentials([string(credentialsId: 'govready_q_api_url', variable: 'Q_API_URL'), string(credentialsId: 'govready_q_api_key', variable: 'Q_API_KEY')]) {
            sh 'curl -F project.file_server.hostname=$(hostname) --header "Authorization:$Q_API_KEY" $Q_API_URL'
        }

        sh './manage.py test guidedmodules'
      }
    }
  }
}