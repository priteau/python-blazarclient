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

from horizon import exceptions
from horizon import forms
from horizon import messages

from blazardashboard import api


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
            'prolong_for': data.get('prolong_for', None),
            'reduce_by': data.get('reduce_by', None),
        }

        try:
            api.blazar.lease_update(self.request, lease_id=lease_id, **fields)
            messages.success(request, _("Lease update started."))
            return True
        except Exception:
            exceptions.handle(request)
