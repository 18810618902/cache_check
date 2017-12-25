#/usr/bin/env python3
#coding:utf-8
#func : create table (node_list, get_adge_info, get_band_vip) ,three tables
#创建三张表，关联查询，得到最终的ip list



import datetime
import os, sys
import requests
import json
import time

from . import log_date
from . import all_defined_api

# from log_date import Logger, d_date
# from all_defined_api import pg_exec


#logs = log_date.Logger()
logs = log_date.Logger()

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)         #把备案脚本的目录放到环境变量中去



def create_all_tables(service_name):
    #print(service_name)
    logs.info("{create_base()/postgre sql [service_with_node_/get_adge_info_/get_band_vip_] } processing......")

    #service_with_node_ 表
    create_str = "CREATE TABLE if not exists service_with_node_" + log_date.d_date + "_" + service_name +\
                  "(node_id INT,node_name VARCHAR(64),service_name VARCHAR(32)) TABLESPACE cdnetworks_beian;"

    #get_edge_info_ 表
    create_str += "CREATE TABLE if not exists get_edge_info_" + log_date.d_date + "_" + service_name +\
                 "(band_id INT, service_name VARCHAR(32)) TABLESPACE cdnetworks_beian;"

    #get_band_vip_ 表
    create_str += "CREATE TABLE if not exists get_band_vip_" + log_date.d_date + "_" + service_name +\
                  "(band_id INT, vips VARCHAR(64), node_name VARCHAR(64)) TABLESPACE cdnetworks_beian;"


    #create_str += "CREATE TABLE select_service (service_name VARCHAR(64)) TABLESPACE cdnetworks_beian;"

    all_defined_api.pg_exec(create_str)

    logs.info("{create_[service_with_node_/get_adge_info_/get_band_vip_]} ended......")


#获取到service组下的node节点，排除掉offline的
def service_with_node(services):
    from conf.oui_api_info import node_list
    # from all_defined_api import post_api_request, pg_exec_values
    from . import  all_defined_api

    logs.info(">>>>>> [ service_with_node ] <<<<<<   processing......")

    post_data = {"info": 0, "service_dns_prefix": services, 'offline':0}
    res = all_defined_api.post_api_request(node_list, post_data)

    service_node_value = []
    if res['status_code'] == 200 and 'data' in res.keys() and 'details' not in res['data'] and len(res['data']) > 0:
        logs.info("service_with_node api is ok")
        for line in res['data']:
            service_node_value.append((str(line['id']).strip(' \t\n\r'), str(line['hostname']).strip(' \t\n\r'), \
                                services))

        insert_pg_command = "INSERT INTO service_with_node_" + log_date.d_date + "_"+services + \
                            " (node_id, node_name, service_name) VALUES (%s, %s, %s)"

        all_defined_api.pg_exec_values(insert_pg_command, service_node_value)
        logs.info(">>>>>> [ import_service_with_node : " + str(services) + "] <<<<<< ended.......")

    else:
        logs.warning("[service_with_node] {" + str(services) + "} may has 0 record.")


#获取这个service组下所有的band_id
def get_edge_info(services):
    from conf.oui_api_info import edge_info
    #from all_defined_api import post_api_request, pg_exec_values
    from . import all_defined_api

    logs.info(">>>>>> [ get_service_info ] <<<<<<   processing......")

    post_data = {"info": 1, "dns_prefix": services}
    res = all_defined_api.post_api_request(edge_info, post_data)

    edge_info_list = []
    if res['status_code'] == 200 and 'data' in res.keys() and 'details' not in res['data'] and len(res['data']) > 0:
        logs.info("get_edge_info api is ok")
        for line in res['data']:
            for band in line['band']:
                edge_info_list.append((str(band['band_id']).strip(' \t\n\r'),  services))
        insert_pg_command = "INSERT INTO get_edge_info_" + log_date.d_date + "_"+services +\
                             " (band_id, service_name) VALUES (%s, %s)"

        all_defined_api.pg_exec_values(insert_pg_command, edge_info_list)
        logs.info(">>>>>> [ get_edge_info : " + str(services) + "] <<<<<< ended.......")

    else:
        logs.warning("[get_edge_info] {" + str(services) + "} may has 0 record.")


#把band对应的vip插入到表中
def get_band_vip(band_id,service_name):
    from conf.oui_api_info import band_vip
    #from all_defined_api import post_api_request, pg_exec_values
    from . import  all_defined_api

    logs.info(">>>>>> [ get_band_vip ] <<<<<<   processing......")

    post_data = {"info": 1, "band_id": band_id, 'offline':1}
    res = all_defined_api.post_api_request(band_vip, post_data)

    band_vip_list = []
    if res['status_code'] == 200 and 'data' in res.keys() and 'details' not in res['data'] and len(res['data']) > 0:
        logs.info("get_band_vip api is ok")
        for line in res['data']:
            for ip in line['vips']:
                #print(ip[0], line['host_name'])
                band_vip_list.append((str(band_id).strip(' \t\n\r'), ip[0], line['host_name']))
        insert_pg_command = "INSERT INTO get_band_vip_" + log_date.d_date + "_"+service_name +\
                            " (band_id, vips, node_name) VALUES (%s, %s, %s)"

        all_defined_api.pg_exec_values(insert_pg_command, band_vip_list)
        logs.info(">>>>>> [ get_band_vip : " + str(band_id) + "] <<<<<< ended.......")

    else:
        logs.warning("[get_band_vip] {" + str(band_id) + "} may has 0 record.")


def nali(ip):

    nali_api = 'http://api.map.baidu.com/location/ip'
    baidu_ak = 'RVeIjB9CgvkxuPXsr8Ql4zgiRTtVSfQG'

    whole_url = nali_api + '?ak=' + baidu_ak + '&' + 'ip=' + ip
    res = requests.get(whole_url)
    # print(whole_url)
    # print(json.loads(res.text.encode().decode()))
    #res.json()
    res = json.loads(res.text.encode().decode())
    if res['status'] == 0:
        res_final = res['content']['address']
        return  res_final
    else:
        return "UNKNOWN"

def data_ruku(service_name, nali):        #接口数据入库
    #from all_defined_api import return_pg_exec
    from . import all_defined_api

    try:
        drop_select_nali_command = 'drop table select_nali;'
        all_defined_api.pg_exec(drop_select_nali_command)
        drop_select_service_command = 'drop table select_service;'
        all_defined_api.pg_exec(drop_select_service_command)
    except Exception as e:
        print('drop  select_service/select_nali table Error:', e)

    create_str = "CREATE TABLE select_service (service_name VARCHAR(64)) TABLESPACE cdnetworks_beian;"
    create_str += "CREATE TABLE select_nali (nali VARCHAR(64)) TABLESPACE cdnetworks_beian;"
    all_defined_api.pg_exec(create_str)
    logs.info("{create_[select_service_/select_nali_]} ended......")

    service_name_ruku = [(service_name, )]
    command_insert_service = "INSERT INTO select_service (service_name) VALUES (%s);"
    all_defined_api.pg_exec_values(command_insert_service, service_name_ruku)
	
    select_nali_ruku = [(nali, )]
    command_insert_service = "INSERT INTO select_nali (nali) VALUES (%s);"
    all_defined_api.pg_exec_values(command_insert_service, select_nali_ruku)


def get_vips_data():        #去获取vips
    logs.info('to get the IP LIST !!!')
    command_select_service = "select * from select_service  order by  service_name  desc limit 1;"
    res = all_defined_api.return_pg_exec(command_select_service)
    service_name = "".join(res[0])
    drop_select_service_command = 'drop table select_service;'
    all_defined_api.pg_exec(drop_select_service_command)

    #这里只用一张表来做实验，后面的  service_name 与 data_time 统一入库
    #service_name = "CL1"
    command_select_date = "select * from time_list_20171211  order by  time  desc limit 1;"
    res = all_defined_api.return_pg_exec(command_select_date)
    choose_date = "".join(res[0])
    print('----------------------------------------',service_name, choose_date)
    command_get_vips = "select vips from get_band_vip_"+ choose_date +"_" +service_name + " as A inner join " \
                       "service_with_node_" + choose_date + "_" +service_name + " as B on A.node_name = B.node_name"

    res = all_defined_api.return_pg_exec(command_get_vips)
    logs.info('get the IP LIST ing ...... !!!')
    ip_list = {}
    command_select_nali = "select * from select_nali order by  nali  desc limit 1;"
    nali_res = all_defined_api.return_pg_exec(command_select_nali)
    nali_on_off = "".join(nali_res[0]).strip()
    print('nali_on_off ===========>',nali_on_off)
    if nali_on_off == 'on':
        logs.info('nali process IP LIST ing ...... !!!')
        for single_ip in res:
            try:
                ip_list["".join(single_ip)] = nali("".join(single_ip))
            except Exception as e:
                print('nali api ERROR:', e)
                time.sleep(1)
                ip_list["".join(single_ip)] = nali("".join(single_ip))
                continue
                

        #all_defined_api.pg_exec("drop table select_service;")
        logs.info('get the IP LIST finished !!!')
        return  ip_list
        #return json.dumps(ip_list.encode().decode())
    else:
        n = 1
        for single_ip in res:
            ip_list[n] = "".join(single_ip)
            n += 1
        logs.info('get the IP LIST finished !!!')
        return  ip_list

    
    drop_select_nali_command = 'drop table select_nali;'
    all_defined_api.pg_exec(drop_select_nali_command)
    


def test():
    # service_name = [("CL2",)]
    # command_insert_service = "INSERT INTO select_service (service_name) VALUES (%s);"
    # all_defined_api.pg_exec_values(command_insert_service, service_name)
    command_select_service = "select service_name from select_service;"
    res = all_defined_api.return_pg_exec(command_select_service)
    service_name = "".join(res[0])
    all_defined_api.pg_exec("drop table select_service;")
    print(service_name)

if __name__ == "__main__":
    # create_all_tables()
    # service_with_node('CL1')
    # get_edge_info('CL1')
     get_band_vip(935, 'CL1')

    # res = data_ruku('336')
    # print(res)
    # # nali('211.152.9.188')
    #test()























