#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Gabriel Morin
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
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
  zone:
    description:
      - The unique ID of the SDN zone.
    required: true
    type: str
  type:
    description:
      - The type of the zone, taking 'evpn', 'faucet', 'qinq', 'simple', 'vlan', 'vxlan'.
    choices: ['evpn', 'faucet', 'qinq', 'simple', 'vlan', 'vxlan']
    type: str
  advertise-subnets:
    description:
      - Advertise evpn subnets if you have silent hosts.
    required: false
    type: bool
  bridge:
    description:
      - Name of the bridge the zone is connected to.
    required: false
    type: str
  bridge-disable-mac-learning:
    description:
      - Disable auto mac learning.
    required: false
    type: bool
  controller:
    description:
      - Frr router name.
    required: false
    type: bool
  dhcp:
    description:
      - Type of the DHCP backend for this zone.
    required: false
    type: str
  disable-arp-nd-suppression
    description:
      - Disable ipv4 arp && ipv6 neighbour discovery suppression.
    required: false
    type: bool
  dns:
    description:
      - Dns api server.
    required: false
    type: str
  dnszone:
    description:
      - Dns domain zone  ex: mydomain.com.
    required: false
    type: str
  dp-id:
    description: 
      - Faucet dataplane id
    required: false
    type: int
  exitnodes:
    description:
      - List of cluster node names.
    required: false
    type: str
  exitnodes-local-routing:
    description:
      - Allow exitnodes to connect to evpn guests.
    required: false
    type: str
  exitnodes-primary:
    description:
      - Force traffic to this exitnode first.
    required: false
    type: str
  ipam:
    description:
      - Use a specific ipam.
    required: false
    type: str
  mac:
    description:
      - Anycast logical router mac address.
    required: false
    type: str
  mtu:
    description:
      - MTU.
    required: false
    type: int
  nodes:
    description:
      - List of cluster node names.
    required: false
    type: str
  peers:
    description:
      - Peers address list.
    required: false
    type: str
  reversedns:
    description:
      - Reverse dns api server.
    required: false
    type: str
  rt-import:
    description:
      - Route-Target import.
    required: false
    type: str
  tag:
    description:
      - Service vlan tag
    required: false
    type: int
  vlan-protocol:
    description:
      - Protocol used for vlaning. Can be either 802.1q or 802.1ad. Defaults on 802.1q.
    required: false
    type: str
  vrf-vxlan:
    description:
      - L3 vni.
    required: false
    type: int
  vxlan-port:
    description:
      - Vxlan tunnel udp port (default 4789).
    required: false
    type: int
requirements:
  - proxmoxer
  - requests
'''

EXAMPLES = r'''
- name: Create a simple zone
  proxmox_sdn_zone:
    state: present
    zone: "zone-01"
    type: simple

- name: Create a VLAN zone
  peoxmox_sdn_zone:
    state: present
    zone: "zone-02"
    bridge: vmbr10


- name: Delete an SDN zone
  proxmox_sdn_zone:
    state: absent
    zone: "zone-02"
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
    
    def create_update_sdn_zone(self, zone_id, zone_infos):
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
            self.proxmox_api.cluster.sdn.zones.post(**zone_infos)
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
        'dhcp': {'type': 'str', 'required': False},
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
    # Params
    zone_id = module.params['zone']
    zone_type = module.params['type']
    if str(module.params['advertise-subnets']).lower() == 'true':
        advertise_subnets = 1
    else:
        advertise_subnets = 0
    if str(module.params['bridge-disable-mac-learning']).lower() == "true":
        bridge_disable_mac_learning = 1
    else:
        bridge_disable_mac_learning = 0
    if str(module.params['exitnodes-local-routing']).lower() == "true":
        exitnodes_local_routing = 1
    else:
        exitnodes_local_routing = 0
    if str(module.params['disable-arp-nd-suppression']).lower() == "true":
        disable_arp_nd_suppression = 1
    else:
        disable_arp_nd_suppression = 0

    # To pass params to creation function
    zone_infos = {
        'zone': zone_id,
        'type': zone_type,
        'advertise-subnets': advertise_subnets,
        'bridge': module.params['bridge'],
        'bridge-disable-mac-learning': bridge_disable_mac_learning,
        'controller': module.params['controller'],
        'dhcp': module.params['dhcp'],
        'digest': module.params['digest'],
        'disable-arp-nd-suppression': disable_arp_nd_suppression,
        'dns': module.params['dns'],
        'dnszone': module.params['dnszone'],
        'dp-id': module.params['dp-id'],
        'exitnodes':module.params['exitnodes'],
        'exitnodes-primary': module.params['exitnodes-primary'],
        'exitnodes-local-routing': exitnodes_local_routing,
        'ipam': module.params['ipam'],
        'mac': module.params['mac'],
        'mtu': module.params['mtu'],
        'nodes': module.params['nodes'],
        'peers': module.params['peers'],
        'reversedns': module.params['reversedns'],
        'rt-import': module.params['rt-import'],
        'tag': module.params['tag'],
        'vlan-protocol': module.params['vlan-protocol'],
        'vrf-vxlan': module.params['vrf-vxlan'],
        'vxlan-port': module.params['vxlan-port'],
    }

    if zone_type == 'simple':
      unexpected_properties = [
        'vlan-protocol',
        'advertise-subnets',
        'exitnodes-local-routing',
        'bridge-disable-mac-learning',
        'disable-arp-nd-suppression'
      ]
      for key in unexpected_properties:
        zone_infos.pop(key, None)

    proxmox = ProxmoxSdnZones(module)

    if state == 'present':
        # API call to create/update a zone
        proxmox.create_update_sdn_zone(zone_id, zone_infos)
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