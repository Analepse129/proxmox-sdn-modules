# proxmox_sdn_* modules
Ansible modules for Proxmox VE SDN features.

Inspired by the work Sergei Antipov (UnderGreen) made for the proxmox_pool module.

## Installing
Download the files in your ansible modules folder.
```
e.g : ~/.ansible/plugins/modules
```

You can find all the releases here :

| Release | Link | News |
|:---:|:---:|---|
|1.0|[github]()|Adding Proxmox SDN zones, vnets and subnets support for Ansible.|

> When the developpement will be fininished and ready, I'll try to get this into the community.general repo.

# How to use the proxmox SDN modules ?
## Intoduction
These modules will help you ansibleizing your SDN configuration inside your Proxmox cluster. For now, it supports the creating, deleting and updating zones, vnets and subnets. The [Proxmox SDN API options](https://pve.proxmox.com/pve-docs/api-viewer/#/cluster/sdn) are all implemented for those functions.

For now, controllers, dns and ipams are still waiting for their implementation and should arrive soon.