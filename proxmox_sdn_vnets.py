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
module: proxmox_sdn_vnet
short_description: Management of SDN vnets in a Proxmox VE cluster
version_added: "1.0.0"
description:
  - Allows you to create, update and delete SDN vnet configurations in a Proxmox VE cluster.
author: "Gabriel Morin (@Analepse129)"
options:
  state:
    description:
      - Define whether the vnet should exist or not, taking 'present', 'absent'.
    choices: ['present', 'absent']
    type: str
  vnet:
    description:
      - The unique ID of the SDN vnet.
    required: true
    type: str
  zone:
    description:
      - The Zone ID that the vnet belongs to.
    required: true
    type: str
requirements:
  - proxmoxer
  - requests
'''

EXAMPLES = r'''
- name: Create a new SDN vnet
  proxmox_sdn_vnet:
    state: present
    vnet_id: myvnet
    zone_id: myzone

- name: Delete an SDN vnet
  proxmox_sdn_vnet:
    state: absent
    vnet_id: myvnet
    zone_id: myzone
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)

class ProxmoxSdnVnets(ProxmoxAnsible):
    
    def is_sdn_vnet_empty(self, vnet_id):
        """Check whether vnet has subnets

        :param vnet_id: str - name of the vnet
        :return: bool - is vnet empty?
        """
        data = self.proxmox_api.cluster.sdn.vnets(vnet_id).subnets.get()
        value = 0
        for subnet in data:
          if subnet['vnet'] == vnet_id:
            value = value + 1
        return True if value == 0 else False
    
    def is_sdn_vnet_existing(self, vnet_id):
        """Check whether vnet already exist

        :param vnet_id: str - name of the vnet
        :return: bool - does vnet exists?
        """
        try:
            vnets = self.proxmox_api.cluster.sdn.vnets.get()
            for vnet in vnets:
                if vnet['vnet'] == vnet_id:
                    return True
            return False
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve vnets: {0}".format(e))
    
    def create_update_sdn_vnet(self, vnet_id, vnet_infos):
        """Create Proxmox VE SDN zone

        :param vnet: str - name of the vnet
        :param comment: str, optional - Description of a zone
        :return: None
        """
        if self.is_sdn_vnet_existing(vnet_id):
            self.module.exit_json(changed=False, vnet=vnet_id, msg="Vnet {0} already exists".format(vnet_id))

        if self.module.check_mode:
            return

        try:
            self.proxmox_api.cluster.sdn.vnets.post(**vnet_infos)
        except Exception as e:
            self.module.fail_json(msg="Failed to create vnet with ID {0}: {1}".format(vnet_id, e))
      
    def delete_sdn_vnet(self, vnet_id):
        """Delete Proxmox VE vnet

        :param vnet_id: str - name of the vnet
        :return: None
        """
        if not self.is_sdn_vnet_existing(vnet_id):
            self.module.exit_json(changed=False, vnet=vnet_id, msg="Vnet {0} doesn't exist".format(vnet_id))

        if self.is_sdn_vnet_empty(vnet_id):
            if self.module.check_mode:
                return

            try:
                self.proxmox_api.cluster.sdn.vnets(vnet_id).delete()
            except Exception as e:
                self.module.fail_json(msg="Failed to delete vnet with ID {0}: {1}".format(vnet_id, e))
        else:
            self.module.fail_json(msg="Can't delete vnet {0} with subnets. Please remove subnets from vnet first.".format(vnet_id))

def main():
    module_args = proxmox_auth_argument_spec()

    sdn_vnets_args = {
        # Ansible
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'query'},
        # Mandatory
        'vnet': {'type': 'str', 'required': True},
        'zone': {'type': 'str', 'required': True},
        # Optionnal
        'alias': {'type': 'str', 'required': False},
        'tag': {'type': 'int', 'required': False},
        'type': {'type': 'str', 'required': False},
        'vlanaware': {'type': 'bool', 'required': False},
    }

    module_args.update(sdn_vnets_args)

    result = {'changed': False, 'message': ''}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # Ansible
    state = module.params['state']
    # Params
    vnet_id = module.params['vnet']
    zone_id = module.params['zone']
    if str(module.params['vlanaware']).lower() == 'true':
        vlanaware = 1
    else:
        vlanaware = 0

    # To pass params to creation function
    vnet_infos = {
        'vnet': vnet_id,
        'zone': zone_id,
        'alias': module.params['alias'],
        'tag': module.params['tag'],
        'type': module.params['type'],
        'vlanaware': vlanaware
    }

    proxmox = ProxmoxSdnVnets(module)

    if state == 'present':
        # API call to create/update a vnet
        proxmox.create_update_sdn_vnet(vnet_id, vnet_infos)
        result['changed'] = True
        result['message'] = 'Creating/updating vnet ID: {}'.format(vnet_id)
    elif state == 'absent':
        # API call to delete a vnet
        result['changed'] = True
        result['message'] = 'Deleting vnet ID: {}'.format(vnet_id)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
