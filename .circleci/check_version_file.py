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

# The version number should match the most recent release
# listed in the CHANGELOG, possibly with "+devel".
DEVEL_BUILD = False
with open("CHANGELOG.md") as f:
	for line in f:
		if re.match(r"^-+\s*$", line):
			# A heading before a version number usually is for
			# "In Development" and indicates this is a development build.
			DEVEL_BUILD = True

		m = re.match(r"^(v\S+) \(.*", line)
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

if DEVEL_BUILD and v.local != "devel":
	print("ERROR: The version number {} should end with +devel to signal that this is a development build.".format(repr(VERSION)))
	sys.exit(1)
