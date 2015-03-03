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

from django.template import defaultfilters as django_filters
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.utils import filters

from functools import partial

from blazardashboard import api

class CreateLease(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Lease")
    url = "horizon:project:leases:create"
    classes = ("btn-create", "btn-primary", "ajax-modal", )
    icon = "plus"
    ajax = True

    def __init__(self, attrs=None, **kwargs):
        kwargs['preempt'] = True
        super(CreateLease, self).__init__(attrs, **kwargs)


class UpdateLease(tables.LinkAction):
    name = "update"
    verbose_name = _("Update Lease")
    url = "horizon:project:leases:update"
    classes = ("btn-create", "ajax-modal")


class DeleteLease(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("Lease")
    data_type_plural = _("Leases")
    classes = ('btn-danger', 'btn-terminate')
    #policy_rules = (("orchestration", "cloudformation:DeleteStack"),)

    def action(self, request, lease_id):
        api.blazar.lease_delete(request, lease_id)

    def allowed(self, request, lease):
        #TODO(pafuent):When action is implemented use this code to hide actions
        #if lease is not None:
            #return lease.action
        return True


class LeasesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Lease name"),
                         link="horizon:project:leases:detail",)
    start_date = tables.Column("start_date", verbose_name=_("Start date"),
                               filters=(filters.parse_isotime,
                                        partial(django_filters.date, arg='Y-m-d H:i T')),)
    end_date = tables.Column("end_date", verbose_name=_("End date"),
                             filters=(filters.parse_isotime,
                                      partial(django_filters.date, arg='Y-m-d H:i T')),)
    action = tables.Column("action", verbose_name=_("Action"),)
    status = tables.Column("status", verbose_name=_("Status"),)
    status_reason = tables.Column("status_reason", verbose_name=_("Reason"),)

    class Meta:
        name = "leases"
        verbose_name = _("Leases")
        table_actions = (CreateLease, DeleteLease, )
        row_actions = (UpdateLease, DeleteLease, )
