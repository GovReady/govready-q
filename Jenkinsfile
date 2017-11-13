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
        sh 'apt-get update && apt-get install -y graphviz unzip pandoc wkhtmltopdf jq chromedriver locales && apt-get clean'
        sh 'sed -i "s/^[# ]*en_US.UTF-8/en_US.UTF-8/" /etc/locale.gen'
        sh '/usr/sbin/locale-gen'
        sh 'pip install -r requirements.txt'
        sh './fetch-vendor-resources.sh'
      }
    }
    stage('Test') {
      steps {
        sh 'PATH=$PATH:/usr/lib/chromium ./manage.py test'
      }
    }
  }
}