# -*- coding: cp936 -*-
'''
Created on 2017年7月4日

@author: c00265801
'''
import sys
import os
import requests
import json


class ecs(object):
    '''
    classdocs
    '''

    conn = None
    login = None
    
    def __init__(self, login):
        '''
        Constructor
        '''
        self.conn = login.get_conn()
        self.login = login
        
        
    def query_servers_detail(self): 
        servers_map = {}  
        project_id = self.login.get_project_id()
        endpoint = "https://ecs.eu-de.otc.t-systems.com" + "/v2.1/%s/servers"%project_id

        headers ={"Content-type": "application/json","Accept": "application/json"}
        headers["X-Auth-Token"] = self.login.get_token()
        
       
        r = requests.get(endpoint, headers = headers)    
    
        #print (r.status_code)
        #print (r.text)   
        
        servers = json.loads(r.text)
        for server in servers['servers']:
            t = self.query_server_detail(server['id'])
            
            servers_map[server['id']] = t
        return servers_map
                
    def query_server_detail(self, serverid):
        project_id = self.login.get_project_id()
        endpoint = "https://ecs.eu-de.otc.t-systems.com" + "/v2.1/%s/servers"%project_id + '/%s'%serverid

        headers ={"Content-type": "application/json","Accept": "application/json"}
        headers["X-Auth-Token"] = self.login.get_token()
        
        #payload = {'name': servername}        
        #r = requests.get(endpoint, params = payload, headers = headers)    
        r = requests.get(endpoint, headers = headers)    
    
        #print (r.status_code)
        #print (r.text)   
        
        server = json.loads(r.text)
        #print (server)   
        return server['server']   
    
    def query_flavor_detail(self, flavor_id):
        flavor = self.conn.compute.find_flavor(flavor_id)
        return flavor           

    def query_image_detail(self, image_id):
        image = self.conn.compute.find_image(image_id)
        return image

    def list_vms_array(self):
        vms = []
        hosts = []
        servers_map = self.query_servers_detail()
        for serverid in servers_map.keys():
            server = servers_map[serverid]
            
            #print(server)
            vm = []
            vm.append(server['name'])
            
            if server['OS-EXT-STS:power_state']:
                vm.append("PoweredOn")
            else:
                vm.append("PoweredOff")  
             
            flavor = self.query_flavor_detail(server['flavor']['id'])      
            vm.append(flavor.vcpus)
            vm.append(int(int(flavor.ram)/1024))
            
            vm.append(server['OS-EXT-SRV-ATTR:host'])
            
            image = self.query_image_detail(server['image']['id'])
            if image:
                vm.append(image.metadata['__os_version'])
            else:
                vm.append('NA')    
            #print(vm)
            
            metadata = server['metadata']
            if 'op_svc_userid' in metadata:
                hosts.append(vm)
            else:   
                vms.append(vm)

        return vms, hosts
    
    def query_routers_detail(self):
        rt_map = {}
        routers = self.conn.network.routers()
        for router in routers:
            rt_map[router.id] = router    
        return rt_map
    
    def query_networks_detail(self):
        nw_map = {}
        networks = self.conn.network.networks()
        for network in networks:
            nw_map[network.id] = network    
        return nw_map
         
    def query_subnets_detail(self):
        sn_map = {}
        subnets = self.conn.network.subnets()
        for subnet in subnets:
            sn_map[subnet.id] = subnet    
        return sn_map  
 
    def query_ips_detail(self):
        ip_map = {}
        ips = self.conn.network.ips()
        for ip in ips:
            ip_map[ip.floating_ip_address] = ip    
        return ip_map      
        
    def list_vms_vpc_array(self):
        vms = []
        vpc_subnet_vm_layout = {}
        
        az_host_vm_layout = {}
        
        rt_map = self.query_routers_detail()
        sn_map = self.query_subnets_detail()
        
        servers_map = self.query_servers_detail()
        for serverid in servers_map.keys():
            server = servers_map[serverid]
            
            vm = []
            
            #add vpc name
            if len(server['addresses']):                
                vpc_id = list(server['addresses'].keys())[0]
                if vpc_id in rt_map.keys():
                    router = rt_map[vpc_id]
                    vm.append(router.name)
                else:
                    vm.append(vpc_id)    
            else:
                vm.append('NA')
               
            
            #add subnet cidr and ip addr and EIP
            t = self.conn.compute.server_interfaces(server['id'])
            if t:    
                flag = 1
                for one in t :
                    fixed_ips = one.fixed_ips[0]
                    subnet_id = fixed_ips['subnet_id']
                    ip_address = fixed_ips['ip_address']
                    pt_id = one.port_id
                    
                    subnet = sn_map[subnet_id]

                    vm.append(subnet.cidr)
                    vm.append(ip_address)
                    
                    floating_ip = self.conn.network.ips(port_id = pt_id)
                    if floating_ip:
                        flagx=1
                        for eip in floating_ip:
                            #print(eip)
                            vm.append(eip.floating_ip_address)
                            flagx = 0
                            break
                        if flagx:
                            vm.append('')
                    else:
                        vm.append('')
                        
                    flag = 0
                    break
                if flag:
                    vm.append('NA')
                    vm.append('NA')  
                    vm.append('')      
            else:
                vm.append('NA')
                vm.append('NA')       
                vm.append('') 
                      

            vm.append(server['name'])
            
            if server['OS-EXT-STS:power_state']:
                vm.append("PoweredOn")
            else:
                vm.append("PoweredOff")  
             
            flavor = self.query_flavor_detail(server['flavor']['id'])      
            vm.append(flavor.vcpus)
            vm.append(int(int(flavor.ram)/1024))
            
            vm.append(server['OS-EXT-SRV-ATTR:host'])
            
            image = self.query_image_detail(server['image']['id'])
            if image:
                vm.append(image.metadata['__os_version'])
            else:
                vm.append('NA')   
            
            vm.append(server['OS-EXT-AZ:availability_zone'])
                
            app_vm = [vm[0], vm[1], vm[4], vm[2], vm[3]]                 
            vms.append(app_vm)            
            
            '''
              layout vpc
            '''

            if vm[0] in vpc_subnet_vm_layout.keys():
                if vm[1] in  vpc_subnet_vm_layout[vm[0]].keys():
                    vpc_subnet_vm_layout[vm[0]][vm[1]].append(vm)
                else:
                    subnet_vms = [vm]
                    vpc_subnet_vm_layout[vm[0]][vm[1]] =  subnet_vms
            else:
                subnet_vms = [vm]
                subnet_map = {vm[1]: subnet_vms}    
                vpc_subnet_vm_layout[vm[0]] = subnet_map    


            '''
              layout az
            '''
            az_index = 10
            host_index = 8     
            if vm[az_index] in az_host_vm_layout.keys():
                if vm[host_index] in  az_host_vm_layout[vm[az_index]].keys():
                    az_host_vm_layout[vm[az_index]][vm[host_index]].append(vm)
                else:
                    host_vms = [vm]
                    az_host_vm_layout[vm[az_index]][vm[host_index]] =  host_vms
            else:
                host_vms = [vm]
                host_map = {vm[host_index]: host_vms}    
                az_host_vm_layout[vm[az_index]] = host_map    
 
        #print(vpc_subnet_vm_layout)  
         
        return vms, vpc_subnet_vm_layout, az_host_vm_layout
         
    """
     test code
    """               
    def list_flavors(self):
        print("List Flavors:")
        for flavor in self.conn.compute.flavors():
            print(flavor) 

    def list_flavors_array(self):
        flavors = []
        for flavor in self.conn.compute.flavors():
            one_flavor = []
            one_flavor.append(flavor.name)
            one_flavor.append(flavor.vcpus )
            one_flavor.append(flavor.ram )
            one_flavor.append(flavor.disk  )
            flavors.append(one_flavor)
        return flavors 
    
                         
    def list_servers(self):
        print ('List servers')
        for server in self.conn.compute.servers():
            print (server)
            #print (server.get_server_interface())
            
            for one in self.conn.compute.server_interfaces(server) :
                print (one)
            for one in self.conn.compute.server_ips(server) :
                print (one)           
            print('')
        

    def list_servers_array_x(self):
        servers = []
        for server in self.conn.compute.servers():
            one_server = []
            one_server.append(server.name)
            one_server.append(server.host_id)
            one_server.append(server.flavor['id'] )
            #print(self.conn.compute.find_flavor(server.flavor['id']))
            one_server.append(server.image['id'] )
            #print(self.conn.compute.find_image(server.image['id']))
            one_server.append(server.status)
            servers.append(one_server)
        return servers
        
    
    def list_vms_arrayX(self):
        vms = []
        for server in self.conn.compute.servers():
            print(server)
            vm = []
            vm.append(server.name)
            
            if server.power_state:
                vm.append("PoweredOn")
            else:
                vm.append("PoweredOff")  
                  
            vm.append(self.conn.compute.find_flavor(server.flavor['id']).vcpus)
            vm.append(int(int(self.conn.compute.find_flavor(server.flavor['id']).ram)/1024))
            vm.append(server.host_id)
            image = self.conn.compute.find_image(server.image['id'])
            if image:
                vm.append(self.conn.compute.find_image(server.image['id']).metadata['__os_version'])
            else:
                vm.append('')    
            #print(vm)
            vms.append(vm)
        return vms  
                       
    def list_vms_vpc_arrayX(self):
        vms = []
        vpc_subnet_vm_layout = {}
        for server in self.conn.compute.servers():
            vm = []
            #add vpc name
            
            if len(server.addresses):                
                vpc_id = list(server.addresses.keys())[0]
                router = self.conn.network.find_router(vpc_id)
                if router:
                    vm.append(router.name)
                else:
                    vm.append(vpc_id)    
            else:
                vm.append('')
               
            
            #add subnet cidr and ip addr
            t = self.conn.compute.server_interfaces(server)
            if t:    
                flag = 1
                for one in t :
                    fixed_ips = one.fixed_ips[0]
                    subnet_id = fixed_ips['subnet_id']
                    ip_address = fixed_ips['ip_address']
                    #port_id = one.port_id
                    
                    subnet = self.conn.network.find_subnet(subnet_id)

                    vm.append(subnet.cidr)
                    vm.append(ip_address)
                    
                    floating_ip = self.conn.network.ips(port_id = one.port_id)
                    if floating_ip:
                        flagx=1
                        for eip in floating_ip:
                            print(eip)
                            vm.append(eip.floating_ip_address)
                            flagx = 0
                            break
                        if flagx:
                            vm.append('')
                    else:
                        vm.append('')
                        
                    flag = 0
                    break
                if flag:
                    vm.append('')
                    vm.append('')  
                    vm.append('')      
            else:
                vm.append('')
                vm.append('')       
                vm.append('') 
            
            
                            
            vm.append(server.name)
            
            if server.power_state:
                vm.append("PoweredOn")
            else:
                vm.append("PoweredOff")  
                  
            vm.append(self.conn.compute.find_flavor(server.flavor['id']).vcpus)
            vm.append(int(int(self.conn.compute.find_flavor(server.flavor['id']).ram)/1024))
            vm.append(server.host_id)
            image = self.conn.compute.find_image(server.image['id'])
            if image:
                vm.append(self.conn.compute.find_image(server.image['id']).metadata['__os_version'])
            else:
                vm.append('')    
            #print(vm)
            vms.append(vm)
            
            if vm[0] in vpc_subnet_vm_layout.keys():
                if vm[1] in  vpc_subnet_vm_layout[vm[0]].keys():
                    vpc_subnet_vm_layout[vm[0]][vm[1]].append(vm)
                else:
                    subnet_vms = [vm]
                    vpc_subnet_vm_layout[vm[0]][vm[1]] =  subnet_vms
            else:
                subnet_vms = [vm]
                subnet_map = {vm[1]: subnet_vms}    
                vpc_subnet_vm_layout[vm[0]] = subnet_map     
 
        print(vpc_subnet_vm_layout)  
         
        return vms
    
    def create_security_groups(self, sg_name):
        #create_SG
        createdSG = self.conn.network.create_security_group(
            name = sg_name
            )
        # open a port.
        self.conn.network.security_group_open_port(createdSG.id, 8080,     protocol='tcp')
        #allow ping
        self.conn.network.security_group_allow_ping(createdSG.id)
        # More detailed rules
        IPV4 = 'IPv4'
        PROTO = 'tcp'
        PORT = 22
        DIR = 'ingress'
        self.conn.network.create_security_group_rule(
            direction=DIR, 
            ethertype=IPV4,
            port_range_max=PORT,
            port_range_min=PORT,
            protocol=PROTO, 
            security_group_id=createdSG.id
            )           
         
    def create_keypair(self, keypair_name, ):
        keypair = self.conn.compute.find_keypair(keypair_name)
        if not keypair:
            print("Create Key Pair:")
            keypair = self.conn.compute.create_keypair(name=keypair_name)
            print(keypair)
            """try:
                os.mkdir(SSH_DIR)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise e
            with open(PRIVATE_KEYPAIR_FILE, 'w') as f:
                f.write("%s" % keypair.private_key)
            os.chmod(PRIVATE_KEYPAIR_FILE, 0o400)"""
            
        return keypair   
                    
    def create_server(self,name, image, flavor, network, key_pair, az):
        try:
            server = self.conn.compute.create_server(name=name, 
                                                     flavor_id=flavor.id, 
                                                     image_id=image.id, 
                                                     key_name=key_pair.name,
                                                     networks=[{"uuid": network.id}],
                                                     availability_zone = az)
            server = self.conn.compute.wait_for_server(server)
        except :
            print("Unexpected error:", sys.exc_info()[0])
            return None
        return server

    def delete_server(self, server):
        self.conn.compute.delete_server(server.id)
        self.conn.compute.wait_for_delete(server)
        
    def get_server_status(self, server):
        self.conn.compute.get_server(server.id).status
        
    def stop_server(self, server):
        self.conn.compute.stop_server(server)
        self.conn.compute.wait_for_server(server,status='SHUTOFF')
        
    def start_server(self, server):
        self.conn.compute.start_server(server)       
        self.conn.compute.wait_for_server(server,status='ACTIVE')    
           
    def reboot_server(self, server, rebootType = 'SOFT'):
        """
        The rebootType value can be HARD or SOFT.
        """
        self.conn.compute.reboot_server(server,rebootType)     
        self.conn.compute.wait_for_server(server,status='ACTIVE')  
        