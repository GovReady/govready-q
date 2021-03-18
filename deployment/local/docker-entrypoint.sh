mkdir -p local

if [ -f "local/first_run.lock" ]; then
    echo "[ + ] Execution of first_run previously completed.  Skipping."
else
    echo "[ + ] Executing first_run"
    python3 install.py --non-interactive --docker
    touch local/first_run.lock


# Start server
echo "[ + ] Starting server"
python3 manage.py runserver 0.0.0.0:8000
