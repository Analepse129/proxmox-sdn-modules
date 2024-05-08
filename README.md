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
|1.0|[github](https://github.com/Analepse129/proxmox-sdn-modules/releases/tag/1.0)|Adding Proxmox SDN zones, vnets and subnets support for Ansible.|

> When the developpement will be fininished and ready, I'll try to get this into the community.general repo.

# How to use the proxmox SDN modules ?
## Intoduction
These modules will help you ansibleizing your SDN configuration inside your Proxmox cluster. For now, it supports the creating, deleting and updating zones, vnets and subnets. The [Proxmox SDN API options](https://pve.proxmox.com/pve-docs/api-viewer/#/cluster/sdn) are all implemented for those functions.

For now, controllers, dns and ipams are still waiting for their implementation and should arrive soon.

## Creating zones
A zone represents a specific layer of network isolation and is typically used to segment the network based on security, function, or organizational needs. Each zone can contain multiple vnets (virtual networks) and is responsible for defining the physical boundaries and the network configuration settings that apply to the networks within it. This isolation helps in enhancing security by restricting network traffic to only the entities within the same zone unless explicitly allowed to communicate outside.

The following attributes are availiable for each zone type while creating zones :

|Option|Mandatory|Type|Definition|Possibilities|
|:---:|:---:|:---:|---|---|
|zone| ✅ |string|*The zone name.*|   |
|type| ✅ |string|*The zone type.*|simple / vlan / qinq / vxlan / evpn |
|mtu| ❌ |integer|*MTU*|   |
|nodes| ❌ |string|*List of nodes of the cluster the zone will be propagated onto. Separate nodes by commas. None is the whole cluster.*||
|ipam| ❌ |string|*Which IPAM to use.*|Whatever IPAM name already configured in Proxmox cluster.|
|state| ✅ |string|*Whether the zone is to be created/left in place or destroyed.*|present / absent|

Each zone type has different availiable options, depending on their needs and specificities. The same table presenting the availiable options for each zone will be present in the zone type examples.

>
>⚠️ Please note: It is mandatory to use the following parameters in every zone you create. These parameters are not mentioned in the examples below to avoid cluttering them:
>   ```
>   api_user: '{{ api_user }}'
>   api_password: '{{ api_password }}'
>   api_host: '{{ api_host }}'
>   ```


### Simple zone
A "simple zone" is a straightforward network configuration that primarily focuses on bridging various network interfaces without complex overlay technologies like VXLAN or VLAN. Simple zones facilitate the connection of virtual machines and containers directly to a physical network, using a standard Linux bridge or an Open vSwitch bridge. This setup is ideal for smaller or less complex environments where basic network segmentation and straightforward connectivity are needed without the additional overhead of more advanced network technologies.

Here is how you can declare it using the ansible plugin :
```
tasks:
    name: create simple zone
    proxmox_sdn_zones:
        zone: mysimplezone
        type: simple
        state: present
```

### VLAN zone
A "VLAN zone" refers to a network configuration that utilizes Virtual LAN (VLAN) technology to segregate and manage traffic within a network. VLAN zones help in creating isolated network segments within a single physical infrastructure, enabling distinct broadcast domains that are managed using VLAN tags. This type of zone is particularly useful for environments requiring enhanced security and network segment management without the need for multiple physical networks, making it ideal for efficiently handling traffic separation and access control in a virtualized environment.

The availiable options for the VLAN zone type are :

|Option|Mandatory|Type|Definition|Possibilities|
|:---:|:---:|:---:|---|---|
|bridge|✅|string|*The bridge the zone will communicate with other zones/networks.*|A bridge existing in proxmox (usually ***vmbrX*** with X an integer) |

Here is how you can declare a VLAN zone using the ansible plugin :
```
tasks:
    name: create VLAN zone
    proxmox_sdn_zones:
        zone: vlanzone
        type: vlan
        bridge: vmbr1
        state: present
```
### QinQ zone
A "QinQ zone" refers to an advanced network configuration that leverages the QinQ technology, also known as 802.1ad or VLAN stacking. This type of zone is used to encapsulate multiple VLAN tags within a single VLAN header, effectively allowing for the nesting of VLANs. QinQ zones are particularly useful for service providers who need to extend VLANs across their networks while maintaining isolation between the services offered to different customers, thereby expanding VLAN capacity and simplifying network management.

The availiable options for the QinQ zone type are :

|Option|Mandatory|Type|Definition|Possibilities|
|:---:|:---:|:---:|---|---|
|bridge|✅|string|*The bridge the zone will communicate with other zones/networks.*|A bridge existing in proxmox (usually ***vmbrX*** with X an integer) |
|tag|✅|integer|*The service vlan tag.*| 1 - 4095|
|vlan-protocol|❌|string|*The protocol used to transport VLANS.*|802.1q / 802.1ad (defaults on 802.1q)|

Here is how you can declare a QinQ zone using the ansible plugin :
```
tasks :
    name : create QinQ zone
    proxmox_sdn_zones:
        zone: myqinqzone
        type: qinq
        bridge: vmbr1
        tag: 1
        vlan-protocol: 802.1q
        state: present
```

### VXLAN zone
A "VXLAN zone" refers to a network configuration that uses Virtual Extensible LAN (VXLAN) technology to create a layer 2 network on top of an underlying layer 3 network. This enables the encapsulation of Ethernet frames within UDP packets, allowing for the creation of a virtualized overlay network across multiple physical hosts. VXLAN zones are ideal for environments where scalability and segment isolation are required across different data centers or locations, providing a method to extend layer 2 connectivity over a broader and more diverse network infrastructure.

The availiable options for the VXLAN zone type are :

|Option|Mandatory|Type|Definition|Possibilities|
|:---:|:---:|:---:|---|---|
|peers|✅|string|*The list of peers' IP addresses seperated by commas.*||


Here is how you can declare a VXLN zone using the ansible plugin :
```
tasks :
    name : create vxlan zone
    proxmox_sdn_zones:
        zone: myvxlanzone
        type: vxlan
        peers: "10.0.1.1,10.0.1.2"
        state: present
```

### EVPN zones
An "EVPN zone" refers to a network configuration that implements Ethernet VPN (EVPN) technology, which utilizes BGP (Border Gateway Protocol) to provide MAC address learning and distribution across a VXLAN network. EVPN zones enhance network scalability and flexibility by enabling layer 2 connectivity across different sites with better control and segmentation capabilities. This is particularly useful for complex deployments requiring robust multi-tenancy support and seamless mobility of workloads across distributed environments.

The options availiable for the EVPN zone type are :

|Option|Mandatory|Type|Definition|Possibilities|
|:---:|:---:|:---:|---|---|
|controller|✅|string|*Name of the EVPN controller for this zone.*|Whatever controller is configured in Proxmox|
|vrf-vxlan|✅|integer|*L3 vni.*||
|mac|❌|string|*Anycast logical router mac address.*|Defaults on "auto"|
|exitnodes|❌|string|*List of cluster nodes names.*||
|exitnodes-primary|❌|string|*First exitnode name for higher priority.*||
|exitnodes-local-routing|❌|boolean|*Allow exitnodes to connect to evpn guests*| true / false |
|advertise-subnets|❌|boolean|*Advertise evpn subnets if you have silent hosts*| true / false |
|disable-arp-nd-suppression|❌|boolean|*Disable ipv4 arp && ipv6 neighbour discovery suppression*| true / false |
|rt-import|❌|string|*Route-Target import*||

Here is how you can declare an EVPN zone using the ansible plugin :
```
tasks :
    name : create evpn zone
    proxmox_sdn_zones:
        zone: myevpnzone
        type: evpn
        controller: mycontroller
        vrf-vxlan: 1001
        mac: <vnet mac address>
        exitnodes: "10.0.1.1, 10.0.1.2"
        exitnodes-primary: "10.0.1.1"
        exitnodes-local-routing: true
        advertise-subnets: true
        disable-arp-nd-suppression: false
        rt-import: <import your route targets here>
        state: present
```

### Deleting a zone
Sometimes, for several reasons, you might have to delete a zone. The procedure is very simple, and is the same for every type of zone. 

Here is how you can delete a zone using the ansible plugin :
```
tasks :
    name : delete a zone
    proxmox_sdn_zones:
        zone: myevpnzone
        state: absent
```

> ⚠️ Please note : a zone is only deletable if it's empty. It means that you have to remove every vnets from it before trying to remove it. 
>
>If you try to delete a zone before it's empty, the ansible task will fail and indicate you to remove the vnets.

## VNETS
A vnet, or virtual network, in Proxmox SDN is used to create a virtualized layer of networking within a zone. Vnets allow for the creation of isolated networks for VMs (Virtual Machines) and containers, enabling users to deploy these entities in a manner that mimics separate physical networks. This is particularly useful for creating development, testing, and production environments that are isolated from one another, thus preventing unintended interactions and enhancing the control over network traffic flow.

### Creating VNETS
While creating a VNET is slightly easier than creating a zone due to the smaller number of options, here are all the availiable ones :

|Option|Mandatory|Type|Definition|Possibilities|
|:---:|:---:|:---:|---|---|
|vnet|✅|string|*Name of the VNET to create.*||
|type|❌|string|*Tpe of the vnet.*| Defaults on "vnet"|
|zone|✅|string|*Name of the zone the VNET will belong to.*||
|alias|❌|string|*The alias of the VNET name.*||
|tag|❌|integer|*The VLAN tag or VXLAN id.*||
|vlanaware|❌|boolean|*Allow vm VLANs to pass through this vnet.*| true / false |

Here is how you can declare a VNET using the ansible plugin :
```
tasks :
    name : create a vnet
    proxmox_sdn_vnets:
        vnet: myvnet
        zone: mysimplezone
        vlanaware: false
        state: present
```

### Deleting a VNET
Sometimes you need to delete a vnet for several reasons. As an exemple, to be able to delete a zone.

The procedure is as easy as for deleting a zone :
```
tasks :
    name : delete a vnet
    proxmox_sdn_vnets:
        vnet: myvnet
        state: absent
```
> ⚠️ Please note : a vnet is only deletable if it's empty. It means that you have to remove every subnets from it before trying to remove it. 
>
>If you try to delete a vnet before it's empty, the ansible task will fail and indicate you to remove the subnets.
## Subnets
A subnet in Proxmox SDN is a subdivision of a vnet. It represents a specific IP address range that can be assigned to the interfaces of VMs and containers within a vnet. Subnets are crucial for efficient IP address management and network organization. They allow network administrators to design a network hierarchy that simplifies routing, enhances security by limiting broadcast traffic, and enables fine-grained control over how resources on the network communicate with each other.

### Creating subnet
Creating a sbnet inside a vnet is as easy as creating the vnet. 

Here are the availiable options :

|Option|Mandatory|Type|Definition|Possibilities|
|:---:|:---:|:---:|---|---|
|subnet|✅|string|*The subnet identifier, cidr notation. e.g: 10.0.0.0/8.*||
|snat|❌|boolean|**| true / false |
|dhcp-dns-server|❌|string|*DNS/DHCP server IP address.*||
|dhcp-range|❌|list|*Ranges for DHCP server.*|`start-address=<ip>,end-address=<ip>`|
|gateway|❌|string|*Gateway IP address.*||
|vnet|✅|string|*Parent vnet identifier.*||
|dnszoneprefix|❌|string|*Prefix for DNS zone.*||

Here is how you can declare a subnet using the ansible plugin :
```
tasks :
    name : delete a vnet
    proxmox_sdn_subnets:
        subnet: "10.0.0.0/24"
        vnet: myvnet
        gateway: "10.0.0.1"
        dhcp-dns-server: "10.200.0.1"
        dhcp-range:
          - start-address=10.0.0.10,end-address=10.0.0.20
          - start-address=10.0.0.30,end-address=10.0.0.40
        snat: true
        state: present
```

### Deleting a subnet
The subnet deletion procedure is very similar to the ones to remove zones and vnets. Here is an example :
```
tasks :
    name : delete a subnet
    proxmox_sdn_subnets:
        subnet: "10.0.0.0/8"
        state: absent
```
