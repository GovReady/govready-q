# encoding: utf-8
# copyright: 2016, GovReady PBC
# license: All rights reserved

title 'CloudFoundry PWS'

control 'cf-1.0' do
  impact 0.7
  title 'tbd'
  desc 'tb'
  tag 'cf'
  ref 'CF Requirements 1.0', uri: 'http://...'

  # Test using the custom gordon_config Inspec resource
  # Find the resource content here: ../libraries/
  describe cf_users do
    it { should exist }
  end
end
