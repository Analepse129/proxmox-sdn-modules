#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Gabriel Morin
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_sdn_zone
short_description: Management of SDN zones in a Proxmox VE cluster
version_added: "1.0.0"
description:
  - Allows you to create, update and delete SDN zones configurations in a Proxmox VE cluster.
author: "Gabriel Morin (@Analepse129)"
Main options:
  state:
    description:
      - Define whether the zone should exist or not, taking 'present', 'absent'.
    choices: ['present', 'absent']
    type: str
  zone_id:
    description:
      - The unique ID of the SDN zone.
    required: true
    type: str
  zone_type:
    description:
      - The type of the zone, taking 'evpn', 'faucet', 'qinq', 'simple', 'vlan', 'vxlan'.
    choices: ['evpn', 'faucet', 'qinq', 'simple', 'vlan', 'vxlan']
    type: str
requirements:
  - proxmoxer
  - requests
'''

EXAMPLES = r'''
- name: Create a new SDN zone
  proxmox_sdn_zone:
    state: present
    zone_id: "zone-02"
    description: "This is a new zone for SDN."

- name: Delete an SDN zone
  proxmox_sdn_zone:
    state: absent
    zone_id: "zone-03"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)

class ProxmoxSdnZones(ProxmoxAnsible):
    
    def is_sdn_zone_empty(self, zone_id):
        """Check whether zone has vnets

        :param zone_id: str - name of the zone
        :return: bool - is zone empty?
        """
        data = self.proxmox_api.cluster.sdn.vnets.get()
        value = 0
        for vnet in data:
          if vnet['zone'] == zone_id:
            value = value + 1
        return True if value == 0 else False
    
    def is_sdn_zone_existing(self, zone_id):
        """Check whether zone already exist

        :param zone_id: str - name of the zone
        :return: bool - does zone exists?
        """
        try:
            zones = self.proxmox_api.cluster.sdn.zones.get()
            for zone in zones:
                if zone['zone'] == zone_id:
                    return True
            return False
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve zones: {0}".format(e))
    
    def create_update_sdn_zone(self, zone_id, zone_type):
        """Create Proxmox VE SDN zone

        :param zone_id: str - name of the zone
        :param comment: str, optional - Description of a zone
        :return: None
        """
        if self.is_sdn_zone_existing(zone_id):
            self.module.exit_json(changed=False, zone=zone_id, msg="Zone {0} already exists".format(zone_id))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.cluster.sdn.zones.post(zone = zone_id,
                                                    type = zone_type,
                                                    advertise_subnets = self.module.params.get('advertise-subnets'),
                                                    bridge = self.module.params.get('bridge'),
                                                    bridge_disable_mac_learning = self.module.params.get('bridge-disable-mac-learning'),
                                                    controller = self.module.params.get('controller'),
                                                    delete = self.module.params.get('delete'),
                                                    dhcp = self.module.params.get('dhcp'),
                                                    digest = self.module.params.get('digest'),
                                                    disable_arp_nd_suppression = self.module.params.get('disable-arp-nd-suppression'),
                                                    dns = self.module.params.get('dns'),
                                                    dnszone = self.module.params.get('dnszone'),
                                                    dp_id = self.module.params.get('dp-id'),
                                                    exitnodes = self.module.params.get('exitnodes'),
                                                    exitnodes_local_routing = self.module.params.get('exitnodes-local-routing'),
                                                    ipam = self.module.params.get('ipam'),
                                                    mac = self.module.params.get('mac'),
                                                    mtu = self.module.params.get('mtu'),
                                                    nodes = self.module.params.get('nodes'),
                                                    peers = self.module.params.get('peers'),
                                                    reversedns = self.module.params.get('reversedns'),
                                                    rt_import = self.module.params.get('rt-import'),
                                                    tag = self.module.params.get('tag'),
                                                    vlan_protocol = self.module.params.get('vlan-protocol'),
                                                    vrf_vxlan = self.module.params.get('vrf-vxlan'),
                                                    vxlan_port = self.module.params.get('vxlan-port'))
        except Exception as e:
            self.module.fail_json(msg="Failed to create zone with ID {0}: {1}".format(zone_id, e))
      
    def delete_sdn_zone(self, zone_id):
        """Delete Proxmox VE zone

        :param zone_id: str - name of the zone
        :return: None
        """
        if not self.is_sdn_zone_existing(zone_id):
            self.module.exit_json(changed=False, zone=zone_id, msg="Zone {0} doesn't exist".format(zone_id))

        if self.is_sdn_zone_empty(zone_id):
            if self.module.check_mode:
                return

            try:
                self.proxmox_api.cluster.sdn.zones(zone_id).delete()
            except Exception as e:
                self.module.fail_json(msg="Failed to delete zone with ID {0}: {1}".format(zone_id, e))
        else:
            self.module.fail_json(msg="Can't delete zone {0} with vnets. Please remove vnets from zone first.".format(zone_id))


def main():
    module_args = proxmox_auth_argument_spec()
    sdn_zone_args = {
        # Ansible
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'query'},
        # Mandatory
        'zone': {'type': 'str', 'required': True},
        'type': {'type': 'str', 'choices': ['evpn', 'faucet', 'qinq', 'simple', 'vlan', 'vxlan'],'required': True},
        # Optionnal
        'advertise-subnets': {'type': 'bool', 'required': False},
        'bridge': {'type': 'str', 'required': False},
        'bridge-disable-mac-learning': {'type': 'bool', 'required': False},
        'controller': {'type': 'str', 'required': False},
        'delete': {'type': 'str', 'required': False},
        'dhcp': {'type': 'enum', 'required': False},
        'digest': {'type': 'str', 'required': False},
        'disable-arp-nd-suppression': {'type': 'bool', 'required': False},
        'dns': {'type': 'str', 'required': False},
        'dnszone': {'type': 'str', 'required': False},
        'dp-id': {'type': 'str', 'required': False},
        'exitnodes': {'type': 'str', 'required': False},
        'exitnodes-local-routing': {'type': 'bool', 'required': False},
        'exitnodes-primary': {'type': 'str', 'required': False},
        'ipam': {'type': 'str', 'required': False},
        'mac': {'type': 'str', 'required': False},
        'mtu': {'type': 'int', 'required': False},
        'nodes': {'type': 'str', 'required': False},
        'peers': {'type': 'str', 'required': False},
        'reversedns': {'type': 'str', 'required': False},
        'rt-import': {'type': 'str', 'required': False},
        'tag': {'type': 'int', 'required': False},
        'vlan-protocol': {'type': 'str', 'choices': ['802.1q', '802.1ad'], 'default': '802.1q'},
        'vrf-vxlan': {'type': 'int', 'required': False},
        'vxlan-port': {'type': 'int', 'required': False},
    }

    module_args.update(sdn_zone_args)

    result = {'changed': False, 'message': ''}

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[("api_token_id", "api_token_secret")],
        required_one_of=[("api_password", "api_token_id")],
        supports_check_mode=True
    )

    # Ansible
    state = module.params['state']
    # Mandatory
    zone_id = module.params['zone']
    zone_type = module.params['type']
    # Optionnal
    

    proxmox = ProxmoxSdnZones(module)

    if state == 'present':
        # API call to create/update a zone
        proxmox.create_update_sdn_zone(zone_id, zone_type)
        result['changed'] = True
        result['message'] = 'Creating/updating zone ID: {}'.format(zone_id)
    elif state == 'absent':
        # API call to delete a zone
        proxmox.delete_sdn_zone(zone_id)
        result['changed'] = True
        result['message'] = 'Deleting zone ID: {}'.format(zone_id)

    module.exit_json(**result)

if __name__ == '__main__':
    main()