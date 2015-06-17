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

import pytz

class CreateForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Create New Lease')

    name = forms.CharField(
        label=_('Name'),
        widget=forms.TextInput()
    )
    start_date = forms.DateTimeField(
        label=_('Start Date'),
        help_text=_('Enter date/with the format Y-M-D'),
        error_messages={
            'invalid': _('Value should be date, formatted Y-M-D'),
        },
        input_formats=['%Y-%m-%d'],
        widget=forms.DateTimeInput(attrs={'placeholder':'yyyy-mm-dd', 'class':'datepicker'}),
    )
    start_time = forms.DateTimeField(
        label=_('Start Time (24 hour)'),
        help_text=_('Enter time with the format h:m (24 hour)'),
        error_messages={
            'invalid': _('Value should be time, formatted h:m (24 hour)'),
        },
        input_formats=['%H:%M'],
        widget=forms.DateTimeInput(attrs={'placeholder':'hh:mm'}),
    )
    end_date = forms.DateTimeField(
        label=_('End Date'),
        help_text=_('Enter date with the format Y-M-D'),
        error_messages={
            'invalid': _('Value should be date, formatted Y-M-D'),
        },
        input_formats=['%Y-%m-%d'],
        widget=forms.DateTimeInput(attrs={'placeholder':'yyyy-mm-dd', 'class':'datepicker'}),
    )
    end_time = forms.DateTimeField(
        label=_('End Time (24 hour)'),
        help_text=_('Enter time with the format h:m (24 hour)'),
        error_messages={
            'invalid': _('Value should be time, formatted h:m (24 hour)'),
        },
        input_formats=['%H:%M'],
        widget=forms.DateTimeInput(attrs={'placeholder':'hh:mm'}),
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
            start_date = data['start_date']
            start_date = start_date.replace(hour=data['start_time'].time().hour, minute=data['start_time'].time().minute)

            end_date = data['end_date']
            end_date = end_date.replace(hour=data['end_time'].time().hour, minute=data['end_time'].time().minute)

            start_date = self.prepare_datetimes(start_date)
            end_date = self.prepare_datetimes(end_date)

            start = start_date.strftime('%Y-%m-%d %H:%M')
            end = end_date.strftime('%Y-%m-%d %H:%M')

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

    def clean(self):
        localtz = pytz.timezone(self.request.session.get('django_timezone', self.request.COOKIES.get('django_timezone', 'UTC')))
        cleaned_create_data = super(CreateForm, self).clean()
        start_date = cleaned_create_data.get("start_date")
        end_date = cleaned_create_data.get("end_date")

        if start_date > end_date:
            raise forms.ValidationError("Start date must be before end date")
        if start_date < localtz.localize(datetime.today()):
            raise forms.ValidationError("Start date must be after today")

        leases = api.blazar.lease_list(self.request)

        for lease in leases:
            if lease['name'] == cleaned_create_data.get("name"):
                raise forms.ValidationError("A lease with this name already exists.")

        return cleaned_create_data

    # makes sure the datetime has the correct timezone and returns it as UTC
    def prepare_datetimes(self, date):
        localtz = pytz.timezone(self.request.session.get('django_timezone', self.request.COOKIES.get('django_timezone', 'UTC')))

        if date.tzinfo == None:
            date = localtz.localize(date)
        if date.tzinfo != localtz:
            date = date.replace(tzinfo=localtz)

        return date.astimezone(pytz.utc)

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
        fields = {
            'name': data.get('name'),
            'prolong_for': data.get('prolong_for', None) or None,
            'reduce_by': data.get('reduce_by', None) or None,
        }

        try:
            api.blazar.lease_update(self.request, lease_id=lease_id, **fields)
            messages.success(request, _("Lease update started."))
            return True
        except Exception:
            exceptions.handle(request)
