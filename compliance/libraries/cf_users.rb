# encoding: utf-8
# author: Peter Burkholder
#
# There are no up-to-date ruby gems for cloudfoundry:
#  - https://github.com/frodenas/cloudfoundry-client - obsolete
#  - https://github.com/cloudfoundry-attic/cfoundry - obsolete
#  - https://github.com/cloudfoundry/cf-uaa-lib - for UAA interaction
#  - https://github.com/cloudfoundry/cf-app-utils-ruby - for ruby apps _IN_ CF to get services, etc.
# so having to use inspec.cmd to `cf curl`

require 'json'

# Custom resource based on the InSpec resource DSL
class CfSpaceUsers < Inspec.resource(1)
  name 'cf_space_roles'
  desc 'parse `cf space-users` to audit who are managers, developers, auditors'
  example "
    describe cf_space_roles('prod') do
      its('managers') { should eq['pburkholder@govready.com','consulting@joshdata.me','gregelin@govready.com']
      its('developers') { should include('secdevops+pivotalprodrelease@govready.com')}
    end
  "

  def initialize(space)
    @space = space
  end

  def info
    return @info if defined?(@info)

    @info = {}
    @info[:type] = 'cf_space_roles'
    @info[:installed] = true
    @info[:developers] = ['secdevops+pivotalprodrelease@govready.com']
    @info
  end

  def managers
    return ['pburkholder@govready.com','consulting@joshdata.me','gregelin@govready.com']
  end

  def developers
    return info[:developers]
  end

  # Expose all info parameters
  def method_missing(name)
    return info[name.to_s]
  end
end
