# encoding: utf-8
# copyright: 2016, GovReady PBC
# license: All rights reserved

title 'CloudFoundry Node Compliance'

control 'papertrail-logging' do
  impact 0.7
  title 'Papertrail Log Drain'
  desc 'Each app instance should be configure with a papertrail log drain'

  describe cf_vcap_services() do
    its(:user_provided) {
       should include('syslog_drain_url')
    }
  end
end

control 'listening-ports' do
  title 'Enumerate listening ports'
  desc 'only SSH and our python apps should be listening'
  impact 0.7

  describe port(2222) do
    its('processes') { should contain_exactly('diego-sshd') }
    it { should be_listening }
  end

  describe port.where { protocol =~ /tcp/ && port >= 8000  && port < 9000 } do
    its('processes') { should contain_exactly('python') }
    it { should  be_listening }
  end
end

control 'non-listening-ports' do
  title 'Ensure no other ports/processes'
  desc 'only SSH and our python apps should be listening'
  impact 0.7

  describe port.where { protocol =~ /tcp/ && port > 0 && port < 2222 } do
    it { should_not be_listening }
  end
  describe port.where { protocol =~ /tcp/ && port > 2222 && port < 8000 } do
    it { should_not be_listening }
  end
  describe port.where { protocol =~ /tcp/ && port >= 9000 } do
    it { should_not be_listening }
  end
end
