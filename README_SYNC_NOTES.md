
# 1. Back up certain key files

Copy protected files to make them easy to recover

cp ./siteapp/settings.py ./siteapp/settings.py.protected
cp ./siteapp/settings_application.py ./siteapp/settings_application.py.protected
cp ./deployment/docker/dockerfile_exec.sh ./deployment/docker/dockerfile_exec.sh.protected

cp ./requirements.in ./requirements.in.protected
cp ./requirements.txt ./requirements.txt.protected
cp fetch-vendor-resources-mesosphere.sh fetch-vendor-resources-mesosphere.sh.protected
cp ./CHANGELOG.md ./CHANGELOG.md.protected
cp ./VERSION ./VERSION.protected

cp .gitignore .gitignore.protected

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

./fetch-vendor-resources.sh

# 5. Update tags

git tag -a v0.9.1.x -m "version 0.9.1.x"
git push origin --tags


CHANGELog
site

# In Mesosphere Environment Repository

cp -r ../govready-q-0.9.1.x-mesosphere/guidedmodules ./.
cp -r ../govready-q-0.9.1.x-mesosphere/docs ./.
cp -r ../govready-q-0.9.1.x-mesosphere/templates ./.
cp -r ../govready-q-0.9.1.x-mesosphere/static_root ./.
cp -r ../govready-q-0.9.1.x-mesosphere/system_settings ./.
cp -r ../govready-q-0.9.1.x-mesosphere/fixtures ./.
cp -r ../govready-q-0.9.1.x-mesosphere/controls ./.
cp -r ../govready-q-0.9.1.x-mesosphere/discussion ./.
cp -r ../govready-q-0.9.1.x-mesosphere/modules ./.
cp -r ../govready-q-0.9.1.x-mesosphere/requirements* ./.
cp -r ../govready-q-0.9.1.x-mesosphere/VERSION ./.
cp -r ../govready-q-0.9.1.x-mesosphere/list-vendor-resources.sh ./.
cp -r ../govready-q-0.9.1.x-mesosphere/siteapp/* ./siteapp/.


origin  (look up remote)


1. CD govready-q
2. git checkout desired branch
2.5 cp CHANGELOG.md CHANGELOG.md.cbp
3. mv ./.git ../.git_prime (to keep .git repo
make sure .git is not in directory to save time when running unix2dos and not to corrupt .git
4. cp -R ../govready-q-new-version/* ./
5. find . -type f -print0 | xargs -0 -n 1 -P 4 unix2dos
6. cp -R ../.git_prime ./.
7. git status
8. # Checkout protected files
git checkout siteapp/settings.py siteapp/settings_application.py deployment/docker/dockerfile_exec.sh
9. Add any new apps into siteapp/settings_application.py
9. Resolve changelog if needed
10. Any new directories also need to to be added to CME artifactory Dockerfile as a directory to copy
NOTE that changes to Dockerfile need to be deployed to each environment.


