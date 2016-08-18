# encoding: utf-8
# copyright: 2016, GovReady PBC
# license: All rights reserved

title 'CloudFoundry Node Compliance'

only_if do
  os[:family]=='debian'
end

include_controls('os-hardening') do
  # Pivotal's Ubuntu incluces several SUID/SGID binaries:
  skip_control "os-06"

  # And some sysctl controls don't apply:
  %w(01 05 06 07 08 09 10 11 17 18 20 21 22 23 24 25 26 27 28 30).each do |ctl|
    skip_control "sysctl-#{ctl}"
  end
end
