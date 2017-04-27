# My project's README

- Setup Evn
mkvirtualenv --python=/usr/local/bin/python3 ami-admin-portal

- Activate Environment
workon ami-admin-portal

- Install library
pip install -r requirements.txt

- Run Server
python manage.py runserver


- Create log file in local
/data/logs/admin-portal/ami-admin-portal.log

- Create setting file
/data/projects/admin-portal/config/platform_settings.py


# Generate SQL for migration file

- List all migrations by apply order

python manage.py showmigrations --plan


- Show SQL command for a specific migration

python manage.py sqlmigrate app_name migration_number


- Generate SQL for all exist migrations (combination of 2 commands above):

python generate_sql.py
