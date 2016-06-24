from django.conf import settings

from datetime import datetime

def sample_function(question, existing_answers):
    import urllib.request, urllib.parse
    import base64, json

    project_url = existing_answers.get("project_url")
    if not project_url:
        raise ValueError("The website URL is not set.")

    # Get authentication credentials for the GovReady CMS API.
    auth_user, auth_pw = settings.GOVREADY_CMS_API_AUTH

    # Ask the GovReady CMS API for informationa about the website.
    try:
        url = "https://plugin.govready.com/v1.0/public/info?" + urllib.parse.urlencode({
            "url": project_url
        })
        req = urllib.request.Request(url)
        req.add_header('authorization', b'Basic ' + base64.b64encode(auth_user.encode("ascii") + b":" + auth_pw.encode("ascii")))
        req.add_header('cache-control', 'no-cache')
        resp = json.loads(urllib.request.urlopen(req).read().decode("utf8"))
    except Exception as e:
        raise ValueError("There was an error running the analysis: " + str(e))

    return {
        "schema": 1,
        "scan_date": datetime.now().isoformat(),
        "url": project_url,
        "result": resp
    }

if __name__ == "__main__":
    import sys, os, rtyaml
    sys.path.insert(0, '.')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'siteapp.settings'
    ret = sample_function(None, { "project_url": sys.argv[1] })
    print(rtyaml.dump(ret))