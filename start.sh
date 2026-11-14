set -eu
python manage.py migrate --noinput
python bootstrap.py
python seed_demo.py
exec gunicorn wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120
