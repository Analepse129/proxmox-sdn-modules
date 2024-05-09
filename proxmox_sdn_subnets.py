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
module: proxmox_sdn_subnet
short_description: Management of SDN subnets in a Proxmox VE cluster
version_added: "1.0.0"
description:
  - Allows you to create, update and delete SDN subnet configurations in a Proxmox VE cluster.
author: "Gabriel Morin (@Analepse129)"
options:
  state:
    description:
      - Define whether the subnet should exist or not, taking 'present' or 'absent'.
    choices: ['present', 'absent']
    type: str
  type:
    description:
      - The type of the subnet.
    required: true
    type: str
  subnet:
    description:
      - The unique ID of the SDN subnet, as form of a CIDR address.
    required: true
    type: str
  vnet:
    description:
      - The VNet ID that the subnet belongs to.
    required: true
    type: str
  'dhcp-dns-server': 
    description:
      - 
    required: false
    type: 
  'dhcp-range':
    description:
      - 
    required: false
    type: 
  'dnszoneprefix':
    description:
      - 
    required: false
    type: 
  'gateway':
    description:
      - 
    required: false
    type: 
  'snat':
    description:
      - 
    required: false
    type: 
requirements:
  - proxmoxer
  - requests
'''

EXAMPLES = r'''
- name: Create a new SDN subnet
  proxmox_sdn_subnet:
    state: present
    subnet_id: 172.16.10.0/24
    vnet_id: myvnet

- name: Delete an SDN subnet
  proxmox_sdn_subnet:
    state: absent
    subnet_id: 172.16.10.0/24
    vnet_id: myvnet
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)

class ProxmoxSdnSubnets(ProxmoxAnsible):
  
  def is_sdn_subnet_existing(self, subnet_id, vnet_id):
      """Check whether subnet already exist

      :param vnet_id: str - name of the vnet
      :param subnet_id: str - name of the subnet
      :return: bool - does subnet exists?
      """
      try:
          subnets = self.proxmox_api.cluster.sdn.vnets(vnet_id).subnets.get()
          for subnet in subnets:
              if subnet['subnet'] == subnet_id:
                  return True
          return False
      except Exception as e:
          self.module.fail_json(msg="Unable to retrieve subnets: {0}".format(e))
  
  def create_update_sdn_subnet(self, subnet_id, vnet_id, subnet_infos):
      """Create Proxmox VE SDN subnet

      :param subnet: str - name of the subnet
      :param vnet_id: str - name of the parent vnet
      :subnet_infos: dict - elements for the api call
      :return: None
      """
      if self.is_sdn_subnet_existing(subnet_id, vnet_id):
          self.module.exit_json(changed=False, vnet=vnet_id, msg="Subnet {0} already exists".format(subnet_id))
      if self.module.check_mode:
          return
      try:
          self.proxmox_api.cluster.sdn.vnets(vnet_id).subnets.post(**subnet_infos)
      except Exception as e:
          self.module.fail_json(msg="Failed to create subnet with ID {0}: {1}".format(subnet_id, e))
    
  def delete_sdn_vnet(self, subnet_id, vnet_id):
      """Delete Proxmox VE subnet

      :param vnet_id: str - name of the vnet
      :param subnet_id: str - name of the subnet
      :return: None
      """
      if not self.is_sdn_subnet_existing(subnet_id, vnet_id):
          self.module.exit_json(changed=False, vnet=vnet_id, msg="Subnet {0} doesn't exist".format(vnet_id))
      if self.is_sdn_vnet_empty(vnet_id):
          if self.module.check_mode:
              self.module.fail_json(msg="Failed to delete subnet with ID {0}: vnet is empty.")    
      else:
        try:
            self.proxmox_api.cluster.sdn.vnets(vnet_id).subnets(subnet_id).delete()
        except Exception as e:
            self.module.fail_json(msg="Failed to delete subnet with ID {0}: {1}".format(subnet_id, e))

def main():
    
    module_args = proxmox_auth_argument_spec()

    sdn_subnets_args = {
        # Ansible
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'required': True},
        # Mandatory
        'subnet': {'type': 'str', 'required': True},
        'type': {'type': 'str', 'default': 'subnet'},
        'vnet': {'type': 'str', 'required': True},
        # Optionnal
        'dhcp-dns-server': {'type': 'str', 'required': False},
        'dhcp-range': {'type': 'list', 'required': False},
        'dnszoneprefix': {'type': 'str', 'required': False},
        'gateway': {'type': 'str', 'required': False},
        'snat': {'type': 'bool', 'required': False},
    }

    module_args.update(sdn_subnets_args)

    result = {'changed': False, 'message': ''}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Ansible
    state = module.params['state']
    # Params
    subnet_id = module.params['subnet']
    subnet_type = module.params['type']
    vnet_id = module.params['vnet']
    if str(module.params['snat']).lower() == "true":
        snat = 1
    else:
        snat = 0

    # To pass params to creation function
    subnet_infos = {
        "subnet": subnet_id,
        "type": subnet_type,
        "vnet": vnet_id,
        "dhcp-dns-server": module.params['dhcp-dns-server'],
        "dhcp-range": module.params['dhcp-range'],
        "dnszoneprefix": module.params['dnszoneprefix'],
        "gateway": module.params['gateway'],
        "snat": snat
    }

    proxmox = ProxmoxSdnSubnets(module)

    if state == 'present':
        # API call to create/update a subnet
        proxmox.create_update_sdn_subnet(subnet_id, vnet_id, subnet_infos)
        result['changed'] = True
        result['message'] = 'Creating/updating subnet ID: {}'.format(subnet_id)
    elif state == 'absent':
        # API call to delete a subnet
        proxmox.delete_sdn_vnet(subnet_id, vnet_id)
        result['changed'] = True
        result['message'] = 'Deleting subnet ID: {}'.format(subnet_id)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
