Blazar Horizon integration
==========================

Overview
--------
OpenStack Reservation Service Horizon integration

This code is not part of the upstream OpenStack python-blazarclient repository.
It was imported from a patch submitted to OpenStack, and since abandoned: https://review.openstack.org/#/c/100661/


Prerequisites
-------------
* Horizon
* Blazar


Configuration
-------------

Blazar Devstack implementation handles the Blazar Dashboard integration


Running in Development
~~~~~~~~~~~~~~~~~~~~~~

To develop this plugin you need to `set up a development instance
of Horizon`_.
Then, after cloning the ``horizon`` branch of this repo, install the
blazar dashboard into the same virtual env:::

    > git clone https://github.com/ChameleonCloud/python-blazarclient.git
    > cd python-blazarclient/contrib/horizon
    > python setup.py install

Finally, add configuration files the ``openstack_dashboard/local/enabled``
directory in horizon so that it registers the dashboard panel. For example:::

    > cat /path/to/horizon/openstack_dashboard/local/enabled/_40_blazar_add_panel_group.py
    PANEL_GROUP = 'reservation'
    PANEL_GROUP_NAME = 'Reservations'
    PANEL_GROUP_DASHBOARD = 'project'

    > cat /path/to/horizon/openstack_dashboard/local/enabled/_50_blazar_leases_panel.py
    PANEL = 'leases'
    PANEL_DASHBOARD = 'project'
    PANEL_GROUP = 'reservation'
    ADD_PANEL = 'blazardashboard.dashboards.project.leases.panel.Leases'
    ADD_INSTALLED_APPS = ['blazardashboard.dashboards.project.leases']

The panel should now be available in the Horizon instance. As you make changes,
reinstall the blazar dashboard and horizon should pick up the changes automatically.


Gantt Chart
~~~~~~~~~~~

The following additional configuration needs to be added to Horizon's
``local_settings.py``:::

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


.. _set up a development instance of Horizon: http://docs.openstack.org/developer/horizon/quickstart.html
