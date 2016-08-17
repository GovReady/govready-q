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

  describe cf_space_roles('prod') do
    its('managers') {
      should eq(['pburkholder@govready.com','consulting@joshdata.me','gregelin@govready.com'])
    }
    its('developers') { should include('secdevops+pivotalprodrelease@govready.com')}
    its('guid') { should eq('secdevops+pivotalprodrelease@govready.com')}
  end
end
