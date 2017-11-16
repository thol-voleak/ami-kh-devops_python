# Going to bitbucket
- Clone all project 
ami-admin-portal
ami-equator-app-config
ami-equator-functional-test

# Edit Config
- Update folder config
(1) Create forder /data/projects/admin-portal/config/
Copy file Chain.pem  and key public from ami-equator-app-config to (1)

- Edit your hosts file sudo nano /etc/hosts:
127.0.0.1       localhost localhost.equator.local
255.255.255.255 broadcasthost
::1             localhost
 
10.99.101.101 dc1-th-alp-eq-mesos-master-01.node.consul             
10.99.101.13 dc1-th-alp-eq-mesos-master-02.node.consul              
10.99.101.156 dc1-th-alp-eq-mesos-master-03.node.consul             
10.99.103.90 dc1-th-alp-eq-mesos-worker-01.node.consul              
10.99.103.100 alp-service-gateway.service.consul                    
192.168.78.100  truemoneydev.true.th                                
192.168.78.101  truemoneydev.dyndns.org truemoneydev.ebusiness.th                               
10.99.101.101 dc1-th-alp-eq-mesos-master-01.node.consul             
10.99.101.13 dc1-th-alp-eq-mesos-master-02.node.consul

- Update your database config(Create database name admin_portal on your local first)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'admin_portal',
        'USER': 'root',
        'PASSWORD': 'Welcome1',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
 
DOMAIN_NAMES = "https://alp-service-gateway.service.consul:8443/"
CERT="/data/projects/admin-portal/config/chain.pem"
 
CLIENTID = "A1234567890123456789012345678901"
CLIENTSECRET = "A123456789012345678901234567890123456789012345678901234567890123"    

- Create log file in local
/data/logs/admin-portal/ami-admin-portal.log

- Create setting file
/data/projects/admin-portal/config/platform_settings.py          

# Setup Environment in Mac OS
- Install package for mac
install brew: 
https://raw.githubusercontent.com/Homebrew/install/master/install
brew install pip
brew install wget
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
pip3 install mysqlclient

# My project's README

- Setup Evn
virtualenv --python=/usr/local/bin/python3 ami-admin-portal

- Activate Environment
source ami-admin-portal/bin/active

- Install library
pip install -r requirements.txt

- Run Server
python manage.py runserver

