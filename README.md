modify settings.py 
SECRET_KEY = '<your secret key>'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '<your database name',
        'USER': 'your database username>',
        'PASSWORD': '<Your database password>',
        'HOST': '<database hostadress>',
        'PORT': '3306',
    }
}
