mkdir -p local

echo "[ + ] Setting up SSH for remote Interpreter use"
/usr/sbin/sshd
export -p > deployment/local/remote_interpreter/env_var.sh

echo "[ + ] Preparing Django Application"
python3 install.py --non-interactive --docker

# Start server
echo "[ + ] Starting server"
python3 manage.py runserver 0.0.0.0:8000
