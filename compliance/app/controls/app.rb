# encoding: utf-8
# copyright: 2016, GovReady PBC
# license: All rights reserved

#title 'CloudFoundry Node Compliance'

control 'staging-info' do
  impact 0.7
  title 'Ensure control works'
  desc 'This control verifies operation of Inspec by checking for existence of a remote file'

  describe file('/home/vcap/staging_info.yml') do
    it { should exist }
  end
  describe file('/etc/hosts') do
    it { should exist }
  end
end

include_controls('os-hardening') do
end
