# python lint.py file.yaml
# python lint.py file1.yaml file2.yaml file3.yaml
# # dry run (no changes)
# python lint.py -n file.yaml
#
# Example:
# python lint.py path/tofile/AC-ACCESS_CONTROL.yaml
#


import argparse
import difflib

import rtyaml


# Parse command-line arguments.
parser = argparse.ArgumentParser(description='Lint some YAML files.')
parser.add_argument('files', nargs='+', help='an integer for the accumulator')
parser.add_argument('-n', dest="dry_run", action='store_true', help='dry run (print diff instead of rewriting file)')
args = parser.parse_args()

# Process each file on the command line.
for fn in args.files:
	# Read and parse the YAML file.
	with open(fn) as f:
		in_text = f.read()
		data = rtyaml.load(in_text)

	# Lint.
	out_text = rtyaml.dump(data)

	# If doing a dry run, show a unified diff.
	if args.dry_run:
		diff = difflib.unified_diff(
			in_text.split("\n"),
			out_text.split("\n"),
			fromfile=fn + " (original)",
			tofile=fn + " (linted)",
			lineterm="")
		for line in diff:
			print(line)
		continue

	# Write back out.
	with open(fn, "w") as f:
		f.write(out_text)
