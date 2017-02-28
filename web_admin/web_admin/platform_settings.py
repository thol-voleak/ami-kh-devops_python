DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

CLIENTID = "A1234567890123456789012345678901"
CLIENTSECRET = "A123456789012345678901234567890123456789012345678901234567890123"
LOGIN_URL = 'http://alp-eq-esg-01.tmn-dev.com/api-gateway/system-user/v1/oauth/token'
