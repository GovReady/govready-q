# It's like GPS but for... compliance!

Ok go:

	pip3 install -r requirements.txt
	deploy/fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py runserver

To deploy, on a fresh machine, create a Unix user named "site" and in its home directory run:

	git clone https://github.com/GovReady/govready-its-like-gps-but-for-compliance q
	cd q
	mkdir local

Then run:

	sudo deployment/setup.sh

If this is truly on a new machine, it will create a new Sqlite database. You'll also see some output instructing you to create a file named `local/environment.json` containing:

	{
	  "debug": true,
	  "host": "q.govready.com",
	  "https": true,
	  "secret-key": "something random here",
	  "static": "/root/public_html"
	}

You can copy the `secret-key` from what you see --- it was generated to be unique.

# Credits / License

Emoji icons by http://emojione.com/developers/.

