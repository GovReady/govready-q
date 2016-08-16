# encoding: utf-8
# copyright: 2016, GovReady PBC
# license: All rights reserved

title 'Gordon example'

control 'gordon-1.0' do
  impact 0.7
  title 'tbd'
  desc 'This control in place to provide sanity check while building CF check'
  tag 'gordon'
  ref 'Gordon Requirements 1.0', uri: 'http://...'

  # Test using the custom gordon_config Inspec resource
  # Find the resource content here: ../libraries/
  describe gordon_config do
    it { should exist }
    its('version') { should eq('1.0') }
    its('file_size') { should <= 20 }
    its('comma_count') { should == 0 }
  end
end
