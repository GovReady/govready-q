# encoding: utf-8
# copyright: 2016, GovReady PBC
# license: All rights reserved

title 'CloudFoundry PWS Compliance'

control 'cf-prod-roles' do
  impact 0.7
  title 'Ensure roles for spaces are appropriate'
  desc 'tb'
  tag 'cf'
  ref 'CF Requirements 1.0', uri: 'http://...'

  describe cf_space_roles('prod') do
    its('managers') {
      should contain_exactly(
        'pburkholder@govready.com',
        'consulting@joshdata.me',
        'gregelin@govready.com'
      )
    }
    its('developers') {
      should contain_exactly('secdevops+pivotalprodrelease@govready.com')
    }
    its('auditors') {
      should contain_exactly('secdevops+pivotalauditor@govready.com')
    }
  end
end

control 'cf-dev-roles' do
  impact 0.7
  title 'Ensure roles for dev space is appropriate'
  desc 'tb'
  tag 'cf'
  ref 'CF Requirements 1.0', uri: 'http://...'

  describe cf_space_roles('dev') do
    its('managers') {
      should contain_exactly(
        'pburkholder@govready.com',
        'consulting@joshdata.me',
        'gregelin@govready.com'
      )
    }
    its('developers') {
      should contain_exactly(
        'secdevops+pivotaldevrelease@govready.com',
        'pburkholder@govready.com',
        'consulting@joshdata.me',
      )
    }
    its('auditors') {
      should contain_exactly('secdevops+pivotalauditor@govready.com')
    }
  end
end

control 'cf-sandbox-roles' do
  impact 0.7
  title 'Ensure roles for sandbox space is appropriate'
  desc 'tb'
  tag 'cf'
  ref 'CF Requirements 1.0', uri: 'http://...'

  describe cf_space_roles('dev') do
    its('managers') {
      should contain_exactly(
        'pburkholder@govready.com',
        'consulting@joshdata.me',
        'gregelin@govready.com'
      )
    }
    its('developers') {
      should contain_exactly(
        'secdevops+pivotaldevrelease@govready.com',
        'pburkholder@govready.com',
        'consulting@joshdata.me',
      )
    }
    its('auditors') {
      should contain_exactly('secdevops+pivotalauditor@govready.com')
    }
  end
end
