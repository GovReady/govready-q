# Removes duplicate id from a module output
# 
# python remove_duplicate_output.py file.yaml
# python remove_duplicate_output.py file1.yaml file2.yaml file3.yaml
# # dry run (no changes)
# python remove_duplicate_output.py -n file.yaml
#
# Example:
# python remove_duplicate_output.py path/tofile/AC-ACCESS_CONTROL.yaml
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

	# Remove duplicates
	current_od_id = ""
	duplicate_ids = []
	for od in range(len(data['output'])):
		print("Processing {} {}".format(od, data['output'][od]['id']))
		if current_od_id == data['output'][od]['id']:
			# We have a duplicate
			print("** duplicate! {}".format(od))
			duplicate_ids.append(od)
			# Removing duplicate item
			# data['output'].remove(od)
			# List is one shorter, 
		else:
			current_od_id = data['output'][od]['id']
	# Remove duplicate items working backward
	# from end of list to avoid messing up index
	for i in reversed(duplicate_ids):
		if args.dry_run:
			print("Will delete {} {}".format(i, data['output'][i]['id']))
		else:
			print("Deleting {} {}".format(i, data['output'][i]['id']))
			data['output'].pop(i)

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
