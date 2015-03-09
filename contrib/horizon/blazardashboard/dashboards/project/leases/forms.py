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


from django.utils.translation import ugettext_lazy as _
from datetime import datetime

from horizon import exceptions
from horizon import forms
from horizon import messages

from blazardashboard import api


class CreateForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Create New Lease')

    name = forms.CharField(
        label=_('Name'),
        widget=forms.TextInput()
    )
    start_date = forms.DateTimeField(
        label=_('Start Date/Time (UTC)'),
        help_text=_('Enter date/time in UTC with the format Y-M-D h:m'),
        error_messages={
            'invalid': _('Value should be UTC date/time, formatted Y-M-D h:m'),
        },
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'placeholder':'yyyy-mm-dd hh:mm'}),
    )
    end_date = forms.DateTimeField(
        label=_('End Date/Time (UTC)'),
        help_text=_('Enter date/time in UTC with the format Y-M-D h:m'),
        error_messages={
            'invalid': _('Value should be UTC date/time, formatted Y-M-D h:m'),
        },
        input_formats=['%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'placeholder':'yyyy-mm-dd hh:mm'}),
    )
    resource_type = forms.ChoiceField(
        label=_('Resource Type'),
        choices=(
            ('physical:host', _('Physical Host')),
        )
    )
    hosts = forms.IntegerField(
        label=_('Number of Hosts'),
        min_value=1,
        initial=1
    )

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

    def handle(self, request, data):
        try:
            name = data['name']
            start = data['start_date'].strftime('%Y-%m-%d %H:%M')
            end = data['end_date'].strftime('%Y-%m-%d %H:%M')
            reservations = [
                {
                    'min': data['hosts'],
                    'max': data['hosts'],
                    'hypervisor_properties': '',
                    'resource_properties': '',
                    'resource_type': data['resource_type'],
                }
            ]
            events = []
            lease = api.blazar.lease_create(request, name, start, end, reservations, events)

            # store created_lease_id in session for redirect in view
            request.session['created_lease_id'] = lease.id

            messages.success(request, _("Lease created successfully."))
            return True
        except Exception as e:
            exceptions.handle(request)


class UpdateForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Update Lease Parameters')

    lease_id = forms.CharField(
        label=_('Lease ID'), widget=forms.widgets.HiddenInput, required=True)
    name = forms.CharField(label=_('Stack Name'), widget=forms.TextInput())
    prolong_for = forms.CharField(
        label=_('Prolong for'),
        widget=forms.TextInput(attrs={'placeholder':
                                      _('Valid suffix are s/h/m/d')}),
        required=False)
    reduce_by = forms.CharField(
        label=_('Reduce by'),
        widget=forms.TextInput(attrs={'placeholder':
                                      ('Valid suffix are s/h/m/d')}),
        required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        #TODO(pafuent): When action is implemented use this code to hide fields
        #initial = kwargs.get('initial', None)
        #if initial:
            #if initial['lease'].action:
                #self.fields['prolong_for'].widget = forms.HiddenInput()
                #self.fields['reduce_by'].widget = forms.HiddenInput()

    def handle(self, request, data):
        lease_id = data.get('lease_id')

        # If prolong_for is just an empty string it will invert the meaning of
        # reduce_by. Make sure empty strings are replaced by None.
        prolong_for = data.get('prolong_for', None)
        if not prolong_for:
            prolong_for = None

        reduce_by = data.get('reduce_by', None)
        if not reduce_by:
            reduce_by = None

        fields = {
            'name': data.get('name'),
            'prolong_for': prolong_for,
            'reduce_by': reduce_by,
        }

        try:
            api.blazar.lease_update(self.request, lease_id=lease_id, **fields)
            messages.success(request, _("Lease update started."))
            return True
        except Exception:
            exceptions.handle(request)
