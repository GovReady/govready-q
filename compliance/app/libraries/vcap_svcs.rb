# encoding: utf-8
# author: Peter Burkholder
# The standard resource, os_env('VCAP_SERVICES'), fails
# to parse because of newlines.

require 'json'

# Custom resource based on the InSpec resource DSL
class CfVcapServices < Inspec.resource(1)
  name 'cf_vcap_services'
  desc 'parse `$VCAP_SERVICES`'
  example "
    describe cf_vcap_services() do
      its('user_provided') { is_expected.to include(:syslog_drain_url) }
    end
  "

  def initialize()
    begin
      @params = {}
      cmd = inspec.command('echo $VCAP_SERVICES')
      @params = JSON.parse(cmd.stdout)
    rescue Exception
      return skip_resource "Cannot parse var VCAP_SERVICES: #{$!}"
    end
  end

  def user_provided
    return @params['user-provided'].shift
  end

  def method_missing(name)
    return params[name]
  end
end
