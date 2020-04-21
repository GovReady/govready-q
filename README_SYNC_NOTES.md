
# 1. Back up certain key files

Copy protected files to make them easy to recover

cp ./CHANGELOG.md ./CHANGELOG.protected
cp ./VERSION ./VERSION.protected
cp ./siteapp/settings.py ./siteapp/settings.py.protected
cp ./siteapp/settings_application.py ./siteapp/settings_application.py.protected
cp fetch-vendor-resources-mesosphere.sh fetch-vendor-resources-mesosphere.sh.protected
cp ./requirements.in ./requirements.in.protected
cp ./requirements.txt ./requirements.txt.protected


# 2. Files that will need editing because they have diverged

Expect resolve these specific pages

.gitignore - perserve inclusion of static files that are ignored in master
    Do not ignore these files
    <<<<<<< HEAD
    =======
    siteapp/static/vendor
    siteapp/static
    >>>>>>> master

CHANGELOG.md
siteapp/settings.py
siteapp/settings_application.py


# 3. Run ./requirements_txt_checker.sh 

Update requirements

# 4 Get Static Files

# 5. Update tags

git tag -a v0.9.1.4 -m "version 0.9.1.4"
git push origin --tags

