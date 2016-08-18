# encoding: utf-8
# copyright: 2016, GovReady PBC
# license: All rights reserved

title 'CloudFoundry Node Compliance'

control 'papertrail-logging' do
  impact 0.7
  title 'Papertrail Log Drain'
  desc 'Each app instance should be configure with a papertrail log drain'

  describe cf_vcap_services() do
    it { should exist }
  end
end

include_controls('os-hardening') do
  skip_control "os-06" # Pivotal's Ubuntu incluces several SUID/SGID binaries
  %w(01 05 06 07 08 09 10 11 17 18 20 21 22 23 24 25 26 27 28 30).each do |ctl|
    skip_control "sysctl-#{ctl}"
  end
end
