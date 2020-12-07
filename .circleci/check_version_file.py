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

if DEVEL_BUILD and v.local != "v999":
	print("ERROR: CHANGELOG has content before a version heading while VERSION file does not include '+devel'. For version releases, VERSION should not include '+devel' and no information should come before the version heading in CHANGELOG. Alternatively, the version number {} should end with +devel to signal that this is a development build.".format(repr(VERSION)))
	sys.exit(1)
