Blazar Horizon integration
==========================

Overview
--------
OpenStack Reservation Service Horizon integration


Prerequisites
-------------
* Horizon
* Blazar


Configuration
-------------

Blazar Devstack implementation handles the Blazar Dashboard integration


Gantt Chart
-----------

The following additional configuration needs to be added to Horizon's
`local_settings.py`:

```
DATABASES = {
    'default': {},
    'blazar': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('BLAZAR_DB_NAME', 'blazar'),
        'HOST': os.environ.get('BLAZAR_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('BLAZAR_DB_PORT', '3306'),
        'USER': os.environ.get('BLAZAR_DB_USER', 'horizon'),
        'PASSWORD': os.environ.get('BLAZAR_DB_PASSWORD', ''),
    }
}
```
