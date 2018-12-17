# Copyright (c) 2014 Bull.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from blazarclient import command
from blazarclient import exception


class ListNetworks(command.ListCommand):
    """Print a list of networks."""
    resource = 'network'
    log = logging.getLogger(__name__ + '.ListNetworks')
    list_columns = ['id', 'network_type', 'physical_network', 'segment_id']

    def get_parser(self, prog_name):
        parser = super(ListNetworks, self).get_parser(prog_name)
        parser.add_argument(
            '--sort-by', metavar="<network_column>",
            help='column name used to sort result',
            default='id'
        )
        return parser


class ShowNetwork(command.ShowCommand):
    """Show network details."""
    resource = 'network'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowNetwork')


class CreateNetwork(command.CreateCommand):
    """Create a network."""
    resource = 'network'
    json_indent = 4
    log = logging.getLogger(__name__ + '.CreateNetwork')

    def get_parser(self, prog_name):
        parser = super(CreateNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--network-type',
            help='Type of physical mechanism associated with the network '
                  'segment. For example: flat, geneve, gre, local, vlan, '
                  'vxlan.'
        )
        parser.add_argument(
            '--physical-network',
            default=None,
            help='Name of the physical network in which the network segment '
                 'is available, required for VLAN networks'
        )
        parser.add_argument(
            '--segment',
            dest='segment_id',
            help='VLAN ID for VLAN networks or Tunnel ID for GENEVE/GRE/VXLAN '
                 'networks'
        )
        parser.add_argument(
            '--extra', metavar='<key>=<value>',
            action='append',
            dest='extra_capabilities',
            default=[],
            help='Extra capabilities key/value pairs to add for the network'
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.network_type:
            params['network_type'] = parsed_args.network_type
        else:
            raise exception.IncorrectNetwork("--network-type is required")

        if parsed_args.physical_network:
            if params.get('network_type') == 'vlan':
                params['physical_network'] = parsed_args.physical_network
            else:
                err_msg = "--physical-network is only valid for VLAN segments"
                raise exception.IncorrectNetwork(err_msg)
        else:
            if params.get('network_type') == 'vlan':
                err_msg = "--physical-network is required for VLAN segments"
                raise exception.IncorrectNetwork(err_msg)
            else:
                params['physical_network'] = None

        if parsed_args.segment_id:
            params['segment_id'] = parsed_args.segment_id
        else:
            raise exception.IncorrectNetwork("--segment is required")

        extras = {}
        if parsed_args.extra_capabilities:
            for capa in parsed_args.extra_capabilities:
                key, _sep, value = capa.partition('=')
                # NOTE(sbauza): multiple copies of the same capability will
                #               result in only the last value to be stored
                extras[key] = value
            params.update(extras)
        return params


class UpdateNetwork(command.UpdateCommand):
    """Update attributes of a network."""
    resource = 'network'
    json_indent = 4
    log = logging.getLogger(__name__ + '.UpdateNetwork')

    def get_parser(self, prog_name):
        parser = super(UpdateNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--extra', metavar='<key>=<value>',
            action='append',
            dest='extra_capabilities',
            default=[],
            help='Extra capabilities key/value pairs to update for the network'
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        extras = {}
        if parsed_args.extra_capabilities:
            for capa in parsed_args.extra_capabilities:
                key, _sep, value = capa.partition('=')
                # NOTE(sbauza): multiple copies of the same capability will
                #               result in only the last value to be stored
                extras[key] = value
            params['values'] = extras
        return params


class DeleteNetwork(command.DeleteCommand):
    """Delete a network."""
    resource = 'network'
    log = logging.getLogger(__name__ + '.DeleteNetwork')
