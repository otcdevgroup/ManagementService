# -*- coding: cp936 -*-

import xlwings as xw
import pandas as pd

from iam import login
from ecs import ecs
from _ast import arg

def layout(sheet_name, vm_map, vm_columns, vm_show_idx):
    sht = xw.Book.caller().sheets[sheet_name]
    sht.clear_contents()

    columns= vm_columns
    HIGH = len(columns)+1
    LVL_1_COL = 1
    LVL_2_COL = 3
    VM_COL = 5
    
    lvl_1_idx = 0
    total_lvl_2 = 0

    for lvl_1_name in vm_map.keys():
        
        lvl_2_idx = 0
        for subnet in vm_map[lvl_1_name].keys():

            
            sht.range(1+total_lvl_2*HIGH, VM_COL).options(transpose=True).value =  columns
            
            vm_idx = 0
            for vm in vm_map[lvl_1_name][subnet]:
                append_vm = []
                for showidx in vm_show_idx:
                    append_vm.append(vm[showidx])
                #append_vm = [vm[4],vm[2], vm[3],vm[5], vm[6], vm[7],vm[8],vm[9]]
                sht.range(1+(total_lvl_2)*HIGH, 6+vm_idx).options(transpose=True).value = append_vm
                vm_idx += 1
                
            sht.range(1+(total_lvl_2)*HIGH, LVL_2_COL).options(transpose=True).value =  [subnet]  
            
            lvl_2_idx += 1    
            total_lvl_2 += 1
            
        sht.range(1+(total_lvl_2-lvl_2_idx)*HIGH, LVL_1_COL).options(transpose=True).value =  [lvl_1_name]    
        
        lvl_1_idx += 1
    
    sht.range(1+(total_lvl_2)*HIGH, LVL_1_COL).options(transpose=True).value =  "/***END***/"  
    sht.range(1+(total_lvl_2)*HIGH, LVL_2_COL).options(transpose=True).value =  "/***END***/"  
    sht.range(1+(total_lvl_2)*HIGH, VM_COL).options(transpose=True).value =  "/***END***/"  

def xl_OTCInfo():
    print('=============START====================')    
    lgi = login.login("")
    
    iam_url = "https://iam.eu-de.otc.t-systems.com/v3"
    
    
    sht = xw.Book.caller().sheets[0]
    name = sht.range('B1').value
    password = sht.range('B2').value
    domainname = sht.range('B3').value

    conn = lgi.create_connection(iam_url,"eu-de",'eu-de',name, password,domainname)
    token = lgi.create_connection_login(iam_url,"eu-de",'eu-de',name, password,domainname)
      
    ecs_test = ecs.ecs(lgi)
    
    vms, hosts = ecs_test.list_vms_array()
    sht = xw.Book.caller().sheets['vm']
    sht.clear_contents()
    df = pd.DataFrame(vms , columns=['Name', 'PowerState','NumCpu','MemoryGB','VMHost','OSVersion','Disks'])
    sht.range('A1').options(index=False).value = df   
    

    sht = xw.Book.caller().sheets['vpc_vm']
    sht.clear_contents()
    vpc_vms_list, vpc_vms_map, az_vms_map = ecs_test.list_vms_vpc_array()
    
    df = pd.DataFrame(vpc_vms_list, columns=['VPC','subnet','Name', 'IP','EIP'])
    sht.range('A1').options(index=False).value = df 

    #vpc_vms_map = {'test_sg_net': {'192.168.2.0/24': [['test_sg_net', '192.168.2.0/24', '192.168.2.124', '', 'co-ss5rictt5-1-k7khuwnorueb-admin_server-pp2tkrerrefi', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Redhat Linux Enterprise 7.3 64bit']], '192.168.1.0/24': [['test_sg_net', '192.168.1.0/24', '192.168.1.90', '', 'voltest-admin_server-k7imw6jaukqk', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Redhat Linux Enterprise 7.3 64bit']]}, 'vpc-ty': {'10.101.2.0/24': [['vpc-ty', '10.101.2.0/24', '10.101.2.4', '', 'maoshifeng1', 'PoweredOn', 1, 4, 'pod01.eu-de-02', 'CentOS 7.3 64bit']], '10.101.4.0/24': [['vpc-ty', '10.101.4.0/24', '10.101.4.16', '', 'DoNotDelZ00187722LVMDemo-yattarget', 'PoweredOn', 8, 128, 'pod03.eu-de-01', 'NA'], ['vpc-ty', '10.101.4.0/24', '10.101.4.17', '160.44.203.168', 'DoNotDelz00187722LVMDemo_Clone_YasHost', 'PoweredOn', 8, 128, 'pod03.eu-de-01', 'NA'], ['vpc-ty', '10.101.4.0/24', '10.101.4.87', '160.44.201.55', 'DoNotDelz00187722Demo_win16', 'PoweredOn', 1, 4, 'pod01.eu-de-01', 'Windows Server 2016 Standard 64bit'], ['vpc-ty', '10.101.4.0/24', '10.101.4.221', '160.44.202.135', 'DoNotDelz00187722LVMDemo_LVMServer', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'NA'], ['vpc-ty', '10.101.4.0/24', '10.101.4.250', '160.44.206.245', 'DoNotDelz00187722LVMnfs', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'NA']]}, 'vpc-sunway-7907': {'192.168.0.0/24': [['vpc-sunway-7907', '192.168.0.0/24', '192.168.0.2', '160.44.192.90', 'sunway-cce-test-node-1', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'EulerOS 2.2 64bit']]}, 'vpc-hotspot': {'192.168.50.0/24': [['vpc-hotspot', '192.168.50.0/24', '192.168.50.166', '', 'test_ULB', 'PoweredOn', 32, 256, 'pod04.eu-de-02', 'Novell SUSE Linux Enterprise Server 11 SP4 64bit']], '192.168.70.0/24': [['vpc-hotspot', '192.168.70.0/24', '192.168.70.34', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_master1_Sec4W', 'PoweredOn', 16, 32, 'pod01.eu-de-01', 'EulerOS 2.2 64bit'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.49', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_core_sQleU', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'EulerOS 2.2 64bit'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.158', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_core_SyZpK', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'EulerOS 2.2 64bit'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.88', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_core_Pa01o', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'EulerOS 2.2 64bit'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.111', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_master2_1E9Ab', 'PoweredOn', 16, 32, 'pod01.eu-de-01', 'EulerOS 2.2 64bit']]}, 'DonotDeleteVpcThomas': {'192.168.0.0/24': [['DonotDeleteVpcThomas', '192.168.0.0/24', '192.168.0.210', '', 'as-config-pft7_MZEY9S35', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Ubuntu 16.04 server 64bit'], ['DonotDeleteVpcThomas', '192.168.0.0/24', '192.168.0.138', '160.44.206.124', 'DoNotDeleteThomas01', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Ubuntu 16.04 server 64bit']]}, 'vpc-wuzhongke': {'10.10.1.0/24': [['vpc-wuzhongke', '10.10.1.0/24', '10.10.1.12', '', 'openstacksdk_test_chenjianyou', 'PoweredOn', 1, 4, 'pod01.eu-de-01', 'CentOS 7.3 64bit']]}, 'NA': {'NA': [['NA', 'NA', 'NA', '', 'hana-az2', 'PoweredOff', 4, 128, 'pod03.eu-de-02', 'Novell SUSE Linux Enterprise Server 11 SP4 64bit']]}, 'vpc-Cloud-video': {'192.168.0.0/24': [['vpc-Cloud-video', '192.168.0.0/24', '192.168.0.111', '160.44.200.217', '注意请勿删除EIP_有德电客户Trail_邹华镭', 'PoweredOn', 8, 32, 'pod01.eu-de-01', 'NA']]}}
    columns=['Name', 'IP', 'EIP', 'PowerState','NumCpu','MemoryGB','VMHost','OSVersion']
    show_idx = [4, 2, 3, 5, 6, 7,8,9]
    layout('vpc_vm_layout', vpc_vms_map, columns, show_idx)

    #az_vms_map ={'eu-de-01': {'pod01.eu-de-01': [['test_sg_net', '192.168.2.0/24', '192.168.2.124', '', 'co-ss5rictt5-1-k7khuwnorueb-admin_server-pp2tkrerrefi', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Redhat Linux Enterprise 7.3 64bit', 'eu-de-01'], ['test_sg_net', '192.168.1.0/24', '192.168.1.90', '', 'voltest-admin_server-k7imw6jaukqk', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Redhat Linux Enterprise 7.3 64bit', 'eu-de-01'], ['vpc-sunway-7907', '192.168.0.0/24', '192.168.0.2', '160.44.192.90', 'sunway-cce-test-node-1', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'EulerOS 2.2 64bit', 'eu-de-01'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.34', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_master1_Sec4W', 'PoweredOn', 16, 32, 'pod01.eu-de-01', 'EulerOS 2.2 64bit', 'eu-de-01'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.49', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_core_sQleU', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'EulerOS 2.2 64bit', 'eu-de-01'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.158', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_core_SyZpK', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'EulerOS 2.2 64bit', 'eu-de-01'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.88', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_core_Pa01o', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'EulerOS 2.2 64bit', 'eu-de-01'], ['vpc-hotspot', '192.168.70.0/24', '192.168.70.111', '', '1b8e8f0f-7ed3-4cdd-9706-988903d6ff00_node_master2_1E9Ab', 'PoweredOn', 16, 32, 'pod01.eu-de-01', 'EulerOS 2.2 64bit', 'eu-de-01'], ['DonotDeleteVpcThomas', '192.168.0.0/24', '192.168.0.210', '', 'as-config-pft7_MZEY9S35', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Ubuntu 16.04 server 64bit', 'eu-de-01'], ['vpc-wuzhongke', '10.10.1.0/24', '10.10.1.12', '', 'openstacksdk_test_chenjianyou', 'PoweredOn', 1, 4, 'pod01.eu-de-01', 'CentOS 7.3 64bit', 'eu-de-01'], ['DonotDeleteVpcThomas', '192.168.0.0/24', '192.168.0.138', '160.44.206.124', 'DoNotDeleteThomas01', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Ubuntu 16.04 server 64bit', 'eu-de-01'], ['vpc-ty', '10.101.4.0/24', '10.101.4.87', '160.44.201.55', 'DoNotDelz00187722Demo_win16', 'PoweredOn', 1, 4, 'pod01.eu-de-01', 'Windows Server 2016 Standard 64bit', 'eu-de-01'], ['vpc-ty', '10.101.4.0/24', '10.101.4.221', '160.44.202.135', 'DoNotDelz00187722LVMDemo_LVMServer', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'NA', 'eu-de-01'], ['vpc-ty', '10.101.4.0/24', '10.101.4.250', '160.44.206.245', 'DoNotDelz00187722LVMnfs', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'NA', 'eu-de-01'], ['vpc-Cloud-video', '192.168.0.0/24', '192.168.0.111', '160.44.200.217', '注意请勿删除EIP_有德电客户Trail_邹华镭', 'PoweredOn', 8, 32, 'pod01.eu-de-01', 'NA', 'eu-de-01']], 'pod03.eu-de-01': [['vpc-ty', '10.101.4.0/24', '10.101.4.16', '', 'DoNotDelZ00187722LVMDemo-yattarget', 'PoweredOn', 8, 128, 'pod03.eu-de-01', 'NA', 'eu-de-01'], ['vpc-ty', '10.101.4.0/24', '10.101.4.17', '160.44.203.168', 'DoNotDelz00187722LVMDemo_Clone_YasHost', 'PoweredOn', 8, 128, 'pod03.eu-de-01', 'NA', 'eu-de-01']]}, 'eu-de-02': {'pod01.eu-de-02': [['vpc-ty', '10.101.2.0/24', '10.101.2.4', '', 'maoshifeng1', 'PoweredOn', 1, 4, 'pod01.eu-de-02', 'CentOS 7.3 64bit', 'eu-de-02']], 'pod04.eu-de-02': [['vpc-hotspot', '192.168.50.0/24', '192.168.50.166', '', 'test_ULB', 'PoweredOn', 32, 256, 'pod04.eu-de-02', 'Novell SUSE Linux Enterprise Server 11 SP4 64bit', 'eu-de-02']], 'pod03.eu-de-02': [['NA', 'NA', 'NA', '', 'hana-az2', 'PoweredOff', 4, 128, 'pod03.eu-de-02', 'Novell SUSE Linux Enterprise Server 11 SP4 64bit', 'eu-de-02']]}}
    columns=['Name', 'IP', 'EIP', 'PowerState','NumCpu','MemoryGB', 'OSVersion']
    show_idx = [4, 2, 3, 5, 6, 7, 9]
    layout('az_vm_layout', az_vms_map, columns, show_idx)   

    show_hosts = []
    columns=['Host', 'Pool','SID ','OS','Filer_data','Aggr_data','Data_size','Filer_log','Aggr_log','Log_size', 'SAP_version ','DB_version']
    for host in hosts:
        show_host = [""]*len(columns)
        show_host[0] = host[0]
        show_host[3] = host[5] 
        for vpc_vm in vpc_vms_list:
            if host[0] == vpc_vm[2]:
                show_host[1] = vpc_vm[0]
                break             
        show_hosts.append(show_host)           
    sht = xw.Book.caller().sheets['host']
    sht.clear_contents()
    df = pd.DataFrame(show_hosts , columns = columns)
    sht.range('A1').options(index=False).value = df    

    print('=============END======================')


SHEET_SPLIT = ":"
CELL_SPLIT = "|"
INCELL_SPLIT = "&"
SHEET_START_FLAG = "Start"
SHEET_END_FLAG = "End"

def layout_txt(sheet_name, vm_map, vm_columns, vm_show_idx, otcinfofile):
    otcinfofile.write("Start%s%s\r\n"%(SHEET_SPLIT, sheet_name))

    columns= vm_columns
    HIGH = len(columns)+1
    LVL_1_COL = 0
    LVL_2_COL = 2
    VM_COL = 4
    
    lvl_1_idx = 0
    total_lvl_2 = 0
    
    

    for lvl_1_name in vm_map.keys():
        
        lvl_1_lines = []
        for l in range(len(vm_map[lvl_1_name].keys())*HIGH):
            lvl_1_lines.append(["","", "", "", ""])   
        lvl_1_lines[0][LVL_1_COL] = lvl_1_name
        
        lvl_2_idx = 0
        for lvl_2_name in vm_map[lvl_1_name].keys():

            lvl_1_lines[lvl_2_idx*HIGH][LVL_2_COL] = lvl_2_name

            
            for i in range(len(columns)):
                lvl_1_lines[lvl_2_idx*HIGH+i][VM_COL] = columns[i]
                
            
            vm_idx = 0
            for vm in vm_map[lvl_1_name][lvl_2_name]:
                append_vm = []
                for showidx in vm_show_idx:
                    append_vm.append(str(vm[showidx]))
                
                for i in range(len(append_vm)):
                    lvl_1_lines[lvl_2_idx*HIGH+i].append(append_vm[i])
                
                vm_idx += 1
                
            
            lvl_2_idx += 1    
            total_lvl_2 += 1
            
        
        for line in lvl_1_lines:
            otcinfofile.write(CELL_SPLIT.join(line))
            otcinfofile.write("\r\n")
        
        lvl_1_idx += 1
    
    otcinfofile.write(CELL_SPLIT.join(["/***END***/", "", "/***END***/", "", "/***END***/"]))
    otcinfofile.write("\r\n")
    otcinfofile.write("End%s%s\r\n"%(SHEET_SPLIT, sheet_name))


def xl_OTCInfo_txt(domain_name, user_name, password, outputfile):
    print('=============START====================')    
        
    lgi = login.login("")
    
    iam_url = "https://iam.eu-de.otc.t-systems.com/v3"
    
    conn = lgi.create_connection(iam_url,"eu-de",'eu-de',user_name, password,domain_name)
    token = lgi.create_connection_login(iam_url,"eu-de",'eu-de',user_name, password,domain_name)
      
    ecs_test = ecs.ecs(lgi)
    
    vms, hosts = ecs_test.list_vms_array()
    vpc_vms_list, vpc_vms_map, az_vms_map = ecs_test.list_vms_vpc_array()
    #vms = [['DoNotDel413170oraclewin08-0719', 'PoweredOn', '2', '8', 'pod01.eu-de-01', 'Windows Server 2008 R2 Enterprise 64bit', 'ecs-6461-volume-0000: /dev/sda, Common I/O, 50G'], ['studio-server-1HEEa9', 'PoweredOn', '1', '4', 'pod01.eu-de-01', 'Windows Server 2012 R2 Standard 64bit', '-: /dev/vda, Common I/O, 100G'], ['nat-server-MsIbTO', 'PoweredOn', '1', '4', 'pod01.eu-de-01', 'Novell SUSE Linux Enterprise Server 12 SP2 64bit', '-: /dev/vda, Common I/O, 100G'], ['hana-node-3Yt2Fg', 'PoweredOn', '8', '256', 'pod03.eu-de-01', 'Novell SUSE Linux Enterprise Server 11 SP4 64bit', 'hana_system_volume: /dev/vda, Ultra-high I/O, 100G\r\nhana_data_volume: /dev/vdb, Ultra-high I/O, 100G\r\nhana_share_volume: /dev/vdc, Ultra-high I/O, 100G\r\nhana_log_volume: /dev/vdd, Ultra-high I/O, 100G\r\nhana_backup_volume: /dev/vde, Ultra-high I/O, 100G'], ['HANA_HEAT_MASTER_zhenghui', 'PoweredOn', '2', '8', 'pod01.eu-de-01', 'CentOS 7.3 64bit', 'HANA_HEAT_MASTER_zhenghui-volume-0000: /dev/sda, High I/O, 10G'], ['l257010-ows-paltform-demo', 'PoweredOn', '2', '8', 'pod01.eu-de-01', 'NA', 'l257010-ows-paltform-demo-volume-0000: /dev/sda, Common I/O, 4G\r\n-: /dev/sdb, Common I/O, 100G'], ['zgq-heat-master', 'PoweredOn', '2', '8', 'pod01.eu-de-01', 'CentOS 7.3 64bit', 'zgq-heat-master-volume-0000: /dev/sda, Common I/O, 4G'], ['APM-ManageEngine-Yuhaizhou', 'PoweredOn', '8', '32', 'pod01.eu-de-01', 'NA', 'APM-ManageEngine-Yuhaizhou-volume-0000: /dev/sda, Common I/O, 150G'], ['ecs-e303-00368462-iTop', 'PoweredOn', '4', '16', 'pod01.eu-de-01', 'Ubuntu 16.04 server 64bit', 'ecs-e303-00368462-iTop-volume-0000: /dev/sda, Common I/O, 100G'], ['zgq-oracle-win', 'PoweredOn', '4', '16', 'pod01.eu-de-01', 'NA', 'zgq-oracle-win-volume-0000: /dev/sda, Common I/O, 30G\r\nzgq-oracle-win-volume-0001 : /dev/sdb, High I/O, 200G'], ['DonotDelete-00368462-EasyOps', 'PoweredOn', '4', '16', 'pod01.eu-de-01', 'CentOS 6.7 64bit', 'ecs-1a6e-volume-0000: /dev/sda, Common I/O, 50G\r\necs-1a6e-volume-0001: /dev/sdb, Common I/O, 200G'], ['DonotDel-c00364418-devtempwindows', 'PoweredOn', '4', '8', 'pod01.eu-de-01', 'NA', 'DonotDel-c00364418-devtemp-volume-0000: /dev/sda, Common I/O, 30G']]
    #hosts = []
    #vpc_vms_list = [['SAPHANA_zhenghui_VPC', '192.168.1.0/24', 'DoNotDel413170oraclewin08-0719', '192.168.1.30', '160.44.200.25'], ['saphana-net-WRXfBe', '10.0.3.0/24', 'studio-server-1HEEa9', '10.0.3.219', '160.44.205.192'], ['saphana-net-WRXfBe', '10.0.3.0/24', 'nat-server-MsIbTO', '10.0.3.8', '160.44.197.248'], ['saphana-net-WRXfBe', '10.0.3.0/24', 'hana-node-3Yt2Fg', '10.0.3.140', ''], ['SAPHANA_zhenghui_VPC', '192.168.0.0/24', 'HANA_HEAT_MASTER_zhenghui', '192.168.0.82', ''], ['l257010-ows-demo', '192.168.1.0/24', 'l257010-ows-paltform-demo', '192.168.1.151', '160.44.200.11'], ['vpc-zgq', '192.168.1.0/24', 'zgq-heat-master', '192.168.1.99', '160.44.205.33'], ['saphana-vpc-6Kn0RS', '10.0.1.0/24', 'APM-ManageEngine-Yuhaizhou', '10.0.1.2', ''], ['vpc-67fd', '192.168.1.0/24', 'ecs-e303-00368462-iTop', '192.168.1.183', '160.44.198.222'], ['vpc-zgq', '192.168.0.0/24', 'zgq-oracle-win', '192.168.0.200', '160.44.201.37'], ['vpc-67fd', '192.168.1.0/24', 'DonotDelete-00368462-EasyOps', '192.168.1.98', '160.44.199.195'], ['vpc-67fd', '192.168.1.0/24', 'DonotDel-c00364418-devtempwindows', '192.168.1.8', '160.44.195.252']]
    #vpc_vms_map = {'SAPHANA_zhenghui_VPC': {'192.168.1.0/24': [['SAPHANA_zhenghui_VPC', '192.168.1.0/24', '192.168.1.30', '160.44.200.25', 'DoNotDel413170oraclewin08-0719', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Windows Server 2008 R2 Enterprise 64bit', 'eu-de-01']], '192.168.0.0/24': [['SAPHANA_zhenghui_VPC', '192.168.0.0/24', '192.168.0.82', '', 'HANA_HEAT_MASTER_zhenghui', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'CentOS 7.3 64bit', 'eu-de-01']]}, 'saphana-net-WRXfBe': {'10.0.3.0/24': [['saphana-net-WRXfBe', '10.0.3.0/24', '10.0.3.219', '160.44.205.192', 'studio-server-1HEEa9', 'PoweredOn', 1, 4, 'pod01.eu-de-01', 'Windows Server 2012 R2 Standard 64bit', 'eu-de-01'], ['saphana-net-WRXfBe', '10.0.3.0/24', '10.0.3.8', '160.44.197.248', 'nat-server-MsIbTO', 'PoweredOn', 1, 4, 'pod01.eu-de-01', 'Novell SUSE Linux Enterprise Server 12 SP2 64bit', 'eu-de-01'], ['saphana-net-WRXfBe', '10.0.3.0/24', '10.0.3.140', '', 'hana-node-3Yt2Fg', 'PoweredOn', 8, 256, 'pod03.eu-de-01', 'Novell SUSE Linux Enterprise Server 11 SP4 64bit', 'eu-de-01']]}, 'l257010-ows-demo': {'192.168.1.0/24': [['l257010-ows-demo', '192.168.1.0/24', '192.168.1.151', '160.44.200.11', 'l257010-ows-paltform-demo', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'NA', 'eu-de-01']]}, 'vpc-zgq': {'192.168.1.0/24': [['vpc-zgq', '192.168.1.0/24', '192.168.1.99', '160.44.205.33', 'zgq-heat-master', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'CentOS 7.3 64bit', 'eu-de-01']], '192.168.0.0/24': [['vpc-zgq', '192.168.0.0/24', '192.168.0.200', '160.44.201.37', 'zgq-oracle-win', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'NA', 'eu-de-01']]}, 'saphana-vpc-6Kn0RS': {'10.0.1.0/24': [['saphana-vpc-6Kn0RS', '10.0.1.0/24', '10.0.1.2', '', 'APM-ManageEngine-Yuhaizhou', 'PoweredOn', 8, 32, 'pod01.eu-de-01', 'NA', 'eu-de-01']]}, 'vpc-67fd': {'192.168.1.0/24': [['vpc-67fd', '192.168.1.0/24', '192.168.1.183', '160.44.198.222', 'ecs-e303-00368462-iTop', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'Ubuntu 16.04 server 64bit', 'eu-de-01'], ['vpc-67fd', '192.168.1.0/24', '192.168.1.98', '160.44.199.195', 'DonotDelete-00368462-EasyOps', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'CentOS 6.7 64bit', 'eu-de-01'], ['vpc-67fd', '192.168.1.0/24', '192.168.1.8', '160.44.195.252', 'DonotDel-c00364418-devtempwindows', 'PoweredOn', 4, 8, 'pod01.eu-de-01', 'NA', 'eu-de-01']]}}
    #az_vms_map = {'eu-de-01': {'pod01.eu-de-01': [['SAPHANA_zhenghui_VPC', '192.168.1.0/24', '192.168.1.30', '160.44.200.25', 'DoNotDel413170oraclewin08-0719', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'Windows Server 2008 R2 Enterprise 64bit', 'eu-de-01'], ['saphana-net-WRXfBe', '10.0.3.0/24', '10.0.3.219', '160.44.205.192', 'studio-server-1HEEa9', 'PoweredOn', 1, 4, 'pod01.eu-de-01', 'Windows Server 2012 R2 Standard 64bit', 'eu-de-01'], ['saphana-net-WRXfBe', '10.0.3.0/24', '10.0.3.8', '160.44.197.248', 'nat-server-MsIbTO', 'PoweredOn', 1, 4, 'pod01.eu-de-01', 'Novell SUSE Linux Enterprise Server 12 SP2 64bit', 'eu-de-01'], ['SAPHANA_zhenghui_VPC', '192.168.0.0/24', '192.168.0.82', '', 'HANA_HEAT_MASTER_zhenghui', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'CentOS 7.3 64bit', 'eu-de-01'], ['l257010-ows-demo', '192.168.1.0/24', '192.168.1.151', '160.44.200.11', 'l257010-ows-paltform-demo', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'NA', 'eu-de-01'], ['vpc-zgq', '192.168.1.0/24', '192.168.1.99', '160.44.205.33', 'zgq-heat-master', 'PoweredOn', 2, 8, 'pod01.eu-de-01', 'CentOS 7.3 64bit', 'eu-de-01'], ['saphana-vpc-6Kn0RS', '10.0.1.0/24', '10.0.1.2', '', 'APM-ManageEngine-Yuhaizhou', 'PoweredOn', 8, 32, 'pod01.eu-de-01', 'NA', 'eu-de-01'], ['vpc-67fd', '192.168.1.0/24', '192.168.1.183', '160.44.198.222', 'ecs-e303-00368462-iTop', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'Ubuntu 16.04 server 64bit', 'eu-de-01'], ['vpc-zgq', '192.168.0.0/24', '192.168.0.200', '160.44.201.37', 'zgq-oracle-win', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'NA', 'eu-de-01'], ['vpc-67fd', '192.168.1.0/24', '192.168.1.98', '160.44.199.195', 'DonotDelete-00368462-EasyOps', 'PoweredOn', 4, 16, 'pod01.eu-de-01', 'CentOS 6.7 64bit', 'eu-de-01'], ['vpc-67fd', '192.168.1.0/24', '192.168.1.8', '160.44.195.252', 'DonotDel-c00364418-devtempwindows', 'PoweredOn', 4, 8, 'pod01.eu-de-01', 'NA', 'eu-de-01']], 'pod03.eu-de-01': [['saphana-net-WRXfBe', '10.0.3.0/24', '10.0.3.140', '', 'hana-node-3Yt2Fg', 'PoweredOn', 8, 256, 'pod03.eu-de-01', 'Novell SUSE Linux Enterprise Server 11 SP4 64bit', 'eu-de-01']]}}

    #print(vms)
    #print(hosts)
    #print (vpc_vms_list)
    #print(vpc_vms_map)
    #print(az_vms_map)
    
    otcinfofile = open(outputfile, 'w')
    
    otcinfofile.write("Start%s%s\r\n"%(SHEET_SPLIT, "vm"))
    columns=['Name', 'PowerState','NumCpu','MemoryGB','VMHost','OSVersion','Disks']
    otcinfofile.write(CELL_SPLIT.join(columns))
    otcinfofile.write("\r\n") 
    for one in vms:
        one[len(one)-1]= one[len(one)-1].replace("\r\n", INCELL_SPLIT)
        line = CELL_SPLIT.join(one)
        otcinfofile.write(line)   
        otcinfofile.write("\r\n")     
    otcinfofile.write("End%s%s\r\n"%(SHEET_SPLIT, "vm"))


    show_hosts = []
    columns=['Host', 'Pool','SID ','OS','Filer_data','Aggr_data','Data_size','Filer_log','Aggr_log','Log_size', 'SAP_version ','DB_version']
    for host in hosts:
        show_host = [""]*len(columns)
        show_host[0] = host[0]
        show_host[3] = host[5] 
        for vpc_vm in vpc_vms_list:
            if host[0] == vpc_vm[2]:
                show_host[1] = vpc_vm[0]
                break             
        show_hosts.append(show_host)           
    otcinfofile.write("Start%s%s\r\n"%(SHEET_SPLIT, "host"))
    otcinfofile.write(CELL_SPLIT.join(columns))
    otcinfofile.write("\r\n") 
    for one in show_hosts:
        line = CELL_SPLIT.join(one)
        otcinfofile.write(line)   
        otcinfofile.write("\r\n")     
    otcinfofile.write("End%s%s\r\n"%(SHEET_SPLIT, "host"))

 
    otcinfofile.write("Start%s%s\r\n"%(SHEET_SPLIT, "vpc_vm"))
    columns=['VPC','subnet','Name', 'IP','EIP']
    otcinfofile.write(CELL_SPLIT.join(columns))
    otcinfofile.write("\r\n")     
    for one in vpc_vms_list:
        line = CELL_SPLIT.join(one)
        otcinfofile.write(line)   
        otcinfofile.write("\r\n")     
    otcinfofile.write("End%s%s\r\n"%(SHEET_SPLIT, "vpc_vm"))
    
    columns=['Name', 'IP', 'EIP', 'PowerState','NumCpu','MemoryGB','VMHost','OSVersion']
    show_idx = [4, 2, 3, 5, 6, 7,8,9]
    layout_txt('vpc_vm_layout', vpc_vms_map, columns, show_idx, otcinfofile)

    columns=['Name', 'IP', 'EIP', 'PowerState','NumCpu','MemoryGB', 'OSVersion']
    show_idx = [4, 2, 3, 5, 6, 7, 9]
    layout_txt('az_vm_layout', az_vms_map, columns, show_idx, otcinfofile) 
    
    otcinfofile.close()  

    print('=============END======================')


import sys, getopt

def main(argv):
    domain_name = ''
    user_name = ''
    password = ''
    outputfile = ''
    help_str = 'Please input params: OTCInfo.py -d <domain> -u <user> -p <password> -f <outputfile>'
    try:
        opts, args = getopt.getopt(argv,"hd:u:p:f:",["domain=","user=", "password=", "outputfile="])
    except getopt.GetoptError:
        print (help_str)
        sys.exit(2)
    #print(opts)
    for opt, arg in opts:
        if opt == '-h':
            print (help_str)
            sys.exit()
        elif opt in ("-d", "--domain"):
            domain_name = arg
        elif opt in ("-u", "--user"):
            user_name = arg
        elif opt in ("-p", "--password"):
            password = arg
        elif opt in ("-f", "--outputfile"):
            outputfile = arg
    if "" != domain_name and "" != user_name and "" != password and "" != outputfile:        
        print ('params is : %s, %s, %s, %s'%(domain_name, user_name, password, outputfile))
        xl_OTCInfo_txt(domain_name, user_name, password, outputfile)
    else:
        print (help_str)
    
    

if __name__ == "__main__":
   main(sys.argv[1:])
