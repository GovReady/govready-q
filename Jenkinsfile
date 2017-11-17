pipeline {
  agent {
    docker {
      image 'python:3'
      args '-p 8001:8001 --network continuousato'
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

        // Run tests, saving results to a temporary file that will be uploaded
        // to the GovReady-Q Compliance Server. Python unittest output goes
        // primarily to standard error, so redirect it to standard output before
        // using tee to get it into a file.
        sh './manage.py test guidedmodules 2>&1 | tee /tmp/pytestresults.txt'

        // Since we're uploading the test into a longtext field, which is expected
        // to be markdown, add hard line breaks.
        sh 'sed -i s/$/\\\\\\\\/ /tmp/pytestresults.txt'
        sh 'echo >> /tmp/pytestresults.txt' // add blank line because trailing \ is not valid as a hard break
        sh 'echo >> /tmp/pytestresults.txt' // add blank line because trailing \ is not valid as a hard break

        withCredentials([string(credentialsId: 'govready_q_api_url', variable: 'Q_API_URL'), string(credentialsId: 'govready_q_api_key', variable: 'Q_API_KEY')]) {
            // Send hostname.
            sh 'curl -F project.file_server.hostname=$(hostname) --header "Authorization:$Q_API_KEY" $Q_API_URL'

            // Send test results.
            sh 'curl -F "project.file_server.login_message=</tmp/pytestresults.txt" --header "Authorization:$Q_API_KEY" $Q_API_URL'
        }
      }
    }
  }
}