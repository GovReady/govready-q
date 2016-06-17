def sample_function(question, existing_answers):
	url = existing_answers.get("project_url")
	if not url:
		raise ValueError("The website URL is not set.")

	try:
		import urllib.request
		resp = urllib.request.urlopen(url)
		headers = resp.info()
	except Exception as e:
		raise ValueError(str(e))

	return {
		"server": headers['Server'],
		"hsts": 'Strict-Transport-Security' in headers,
	}
