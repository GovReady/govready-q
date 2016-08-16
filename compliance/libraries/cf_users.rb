# There are no up-to-date ruby gmes for cloudfoundry:
#  - https://github.com/frodenas/cloudfoundry-client - obsolete
#  - https://github.com/cloudfoundry-attic/cfoundry - obsolete
#  - https://github.com/cloudfoundry/cf-uaa-lib - for UAA interaction
#  - https://github.com/cloudfoundry/cf-app-utils-ruby - for ruby apps _IN_ CF to get services, etc.

# Custom resource based on the InSpec resource DSL
class CfSpaceUsers < Inspec.resource(1)
  name 'cf_space_roles'


  desc "
   parse `cf space-users` to audit who are managers, developers, auditors
  "

  example "
    describe cf_space_roles do
      its('managers') { should eq[a@b, c@d]
      its('file_size') { should > 1 }
    end
  "

  # Load the configuration file on initialization
  def initialize
    @params = {}
    @path = '/tmp/gordon/config.yaml'
    @file = inspec.file(@path)
    return skip_resource "Can't find file \"#{@path}\"" if !@file.file?

    # Protect from invalid YAML content
    begin
      @params = YAML.load(@file.content)
      # Add two extra matchers
      @params['file_size'] = @file.size
      @params['file_path'] = @path
      @params['ruby'] = 'RUBY IS HERE TO HELP ME!'
    rescue Exception
      return skip_resource "#{@file}: #{$!}"
    end
  end

  # Example method called by 'it { should exist }'
  # Returns true or false from the 'File.exists?' method
  def exists?
    return File.exists?(@path)
  end

  # Example matcher for the number of commas in the file
  def comma_count
    text = @file.content
    return text.count(',')
  end

  # Expose all parameters
  def method_missing(name)
    return @params[name.to_s]
  end
end
