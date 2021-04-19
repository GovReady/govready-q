mkdir -p local

echo "[ + ] Setting up SSH for remote Interpreter use"
if [[ ! -d /usr/src/app/deployment/local/ssh ]]; then
    echo "Configuring SSH Daemon"
    mkdir /usr/src/app/deployment/local/ssh
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
    ssh-keygen -A
    chmod -R 400 /etc/ssh
    cp /etc/ssh /usr/src/app/deployment/local -r
fi
/usr/sbin/sshd
export -p > deployment/local/remote_interpreter/env_var.sh


echo "[ + ] Running checks"
pip3 install -r requirements.txt --ignore-installed

echo "[ + ] Running checks"
./manage.py check --deploy

echo "[ + ] Migrating Database"
./manage.py migrate

echo "[ + ] Preparing Data"
./manage.py load_modules
./manage.py first_run --non-interactive > tmp/first_run.txt

echo "[ + ] Setting up GovReady-Q sample project if none exists"
./manage.py load_govready_ssp


cat first_run.txt | python3 -c "import sys; data=sys.stdin.read(); import re; tmp=re.findall('Created administrator account \(username: (admin)\) with password: ([a-zA-Z0-9#?\!\@\$%^&*-]+)',data); print(f'Created Administrator Account - {tmp[0][0]} / {tmp[0][1]} - This is the only time you will see this message so make sure to write this down\!') if tmp else ''"

echo "[ + ] Starting server"
./manage.py runserver 0.0.0.0:8000
