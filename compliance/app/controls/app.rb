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
