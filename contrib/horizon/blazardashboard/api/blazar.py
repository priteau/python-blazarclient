# Copyright 2014 Intel Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from climateclient import client as blazar_client

from openstack_dashboard.api import base

LOG = logging.getLogger(__name__)
LEASE_DATE_FORMAT = "%Y-%m-%d %H:%M"


class Lease(base.APIDictWrapper):
    """Represents one Blazar lease."""
    ACTIONS = (CREATE, DELETE, UPDATE, START, STOP
               ) = ('CREATE', 'DELETE', 'UPDATE', 'START', 'STOP')

    STATUSES = (IN_PROGRESS, FAILED, COMPLETE
                ) = ('IN_PROGRESS', 'FAILED', 'COMPLETE')

    _attrs = ['id', 'name', 'start_date', 'end_date', 'user_id', 'project_id',
              'before_end_notification', 'action', 'status', 'status_reason']

    def __init__(self, apiresource):
        super(Lease, self).__init__(apiresource)

    #@property
    #def xxx(self):
        #return self._xxx


def blazarclient(request):
    """Initialization of Blazar client."""

    endpoint = base.url_for(request, 'reservation')
    LOG.debug('blazarclient connection created using token "%s" '
              'and endpoint "%s"' % (request.user.token.id, endpoint))
    return blazar_client.Client(climate_url=endpoint,
                                auth_token=request.user.token.id)


def lease_list(request):
    """List the leases."""
    leases = blazarclient(request).lease.list()
    return [Lease(l) for l in leases]


def lease_get(request, lease_id):
    """Get a lease."""
    lease = blazarclient(request).lease.get(lease_id)
    return Lease(lease)

def lease_create(request, name, start, end, reservations, events):
    """Create a lease."""
    lease = blazarclient(request).lease.create(name, start, end, reservations, events)
    return Lease(lease)

def lease_update(request, lease_id, **kwargs):
    """Update a lease."""
    lease = blazarclient(request).lease.update(lease_id, **kwargs)
    return Lease(lease)


def lease_delete(request, lease_id):
    """Delete a lease."""
    blazarclient(request).lease.delete(lease_id)
