#!/bin/bash
echo $country_code
echo $env_name
echo $app_name
app_version=$(cat /image_info/app_version)
echo $app_version

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

source /opt/rh/python27/enable && export X_SCLS="`scl enable python27 'echo $X_SCLS'`"

echo '- Copy platform_settings.py file'
su -s /bin/sh apache -c "cd /data/projects/triple-a/config && wget https://s3-ap-southeast-1.amazonaws.com/acm-ecs-configuration-repo/$country_code/$env_name/$app_name/$app_name-$app_version/__init__.py"
su -s /bin/sh apache -c "cd /data/projects/triple-a/config && wget https://s3-ap-southeast-1.amazonaws.com/acm-ecs-configuration-repo/$country_code/$env_name/$app_name/$app_name-$app_version/platform_settings.py"
su -s /bin/sh apache -c "rm -rf /var/www/django/ami-admin-portal/web_admin/web_admin/platform_settings.py"
su -s /bin/sh apache -c "cp /data/projects/ami-admin-portal/config/platform_settings.py /var/www/django/ami-admin-portal/web_admin/web_admin/platform_settings.py"

echo '- Collect static'
su -s /bin/sh apache -c "python /var/www/django/web_admin/web_admin/manage.py collectstatic --noinput"

echo '- Prepare httpd Server'
python /var/www/django/web_admin/web_admin/manage.py runmodwsgi --user apache --group apache --port 9980 \
--log-directory=/data/logs/triple-a/ --access-log --server-root=/opt/httpd --setup-only --process-name=ami-admin-portal \
--threads 200

echo "Start Web Server"
/opt/httpd/apachectl start -DFOREGROUND