mkdir -p local

echo "[ + ] Setting up SSH for remote Interpreter use"
if [[ ! -d /usr/src/app/deployment/local/ssh ]]; then
    echo "Configuring SSH Daemon"
    mkdir /usr/src/app/deployment/local/ssh
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
    ssh-keygen -A
    chmod -R 400 /etc/ssh
    cp /etc/ssh /usr/src/app/deployment/local -r
else
    cp /usr/src/app/deployment/local/ssh/* /etc/ssh -r
fi
/usr/sbin/sshd
export -p > deployment/local/remote_interpreter/env_var.sh

echo "[ + ] Preparing Django Application"
python3 install.py --non-interactive --docker

# Start server
echo "[ + ] Starting server"
python3 manage.py runserver 0.0.0.0:8000
