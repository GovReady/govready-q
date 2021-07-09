import sys
import re
from pkg_resources import parse_version

with open("VERSION") as f:
	VERSION = f.read().strip()

# Parse. Valid versions yield a SetupToolsVersion object.
# Invalid versions yield SetupToolsLegacyVersion objects.
v = parse_version(VERSION)

if "Legacy" in type(v).__name__:
	print("ERROR: The version number {} is not a PEP440-compliant version number.".format(repr(VERSION)))
	sys.exit(1)

# The version number from file `VERSION` should match the first (e.g., most recent)
# release listed at top of file `CHANGELOG.md`, possibly with "+devel".
# Any change information coming before version information indicates
# version and changelog are not synchronized
DEVEL_BUILD = False
with open("CHANGELOG.md") as f:
	for line in f:
		if re.match(r"^(v\S+-dev) \(.*", line) or re.match(r"^-+\s*$", line) or v.is_prerelease:
			DEVEL_BUILD = True

		m = re.match(r"^(v\S+-dev) \(.*|^(v\S+) \(.*", line)
		if m:
			CURRENT_VERSION = m.group(1)
			break

	else:
		# No version detected.
		print("ERROR: No release version found in CHANGELOG.md.")
		sys.exit(1)

if not DEVEL_BUILD and v.local:
	print("ERROR: The version number {} is not a PEP440-compliant public version number. It should not have a + component.".format(repr(VERSION)))
	sys.exit(1)

# check to ensure that if either the CHANGELOG or VERSION indicates a development build, the other does so as well
if not DEVEL_BUILD and v.is_prerelease:
	print("The VERSION file indicates a development build version of {}, while the CHANGELOG does not, indicating a version of {}.".format(VERSION, CURRENT_VERSION))
	sys.exit(1)
elif DEVEL_BUILD and not v.is_prerelease:
	print("The VERSION file does not indicate a development build, with a version of {}, while the CHANGELOG does indicate a development build, with a version of {}.".format(VERSION, CURRENT_VERSION))
	sys.exit(1)
