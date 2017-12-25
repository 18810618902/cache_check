#/usr/bin/env python3
#coding:utf-8
#func : 把所有的service信息都入库，


import datetime
import os, sys
import requests
import json
import importlib
import time
import multiprocessing
from multiprocessing import Pool


# from . import log_date
# from . import all_defined_api

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)         #把脚本的目录放到环境变量中去

from bin.log_date import Logger
from bin.all_defined_api import pg_exec, return_pg_exec, pg_exec_values


importlib.reload(datetime)
t_date = datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d")


#logs = log_date.Logger()
logs = Logger()




def all_serive_info_input_database(service_name):
    from bin.final_result import create_all_tables, get_edge_info, service_with_node, get_band_vip
    #创建表,每个服务组会对应如下的三张表
    service_name = ''.join(service_name).replace('-','_')
    create_all_tables(service_name)
    #信息入库
    '''
         band_id | service_name 
        ---------+--------------
             935 | CL1
    '''
    get_edge_info(service_name)
    """
    信息入库
        get_edge_info_20171206_cl1
        service_with_node_20171206_cl1
         node_id |         node_name          | service_name 
        ---------+----------------------------+--------------
            9381 | h0-s1.p0-mxz.cdngp.net     | CL1
            9637 | h0-s1.p0-yiw.cdngp.net     | CL1
    """
    service_with_node(service_name)
    """
        get_band_vip_20171206_cl1 ;
         band_id |      vips       |         node_name          
        ---------+-----------------+----------------------------
             935 | 115.238.249.215 | h0-s1025.p2-hgh.cdngp.net
             935 | 115.238.253.196 | h0-s1028.p2-hgh.cdngp.net

    """

    command_get_band_id = 'select band_id from get_edge_info_' + t_date + "_" + service_name
    band_id_list = return_pg_exec(command_get_band_id)
    for band in band_id_list:
        band_sigle_id = list(band)[0]

        try:
            get_band_vip(band_sigle_id, service_name)  # 把service组下的band id 下的vips 都入库
        except Exception as e:
            print('EORROR:',e)
            for i in range(600):
               print('you need wait for 600s: ', i , 's')
               time.sleep(1)
            get_band_vip(band_sigle_id, service_name)
            continue






if __name__ == '__main__':
    command_str = 'select service_name from service_list_20171211'
    services = return_pg_exec(command_str)
    print(services)

    insert_time_command = "INSERT INTO time_list_20171211 (time) VALUES (%s)"
    pg_exec_values(insert_time_command, [(t_date,)])

    c_count = multiprocessing.cpu_count()
    if c_count <= 4:
        c_count = 3
    elif c_count >= 8:
        c_count = 6

    with Pool(processes = c_count) as pool:
        pool.map(all_serive_info_input_database, services)
        pool.close()
        pool.join()

