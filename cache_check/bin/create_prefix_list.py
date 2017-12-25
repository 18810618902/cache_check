#/usr/bin/env python3
#coding:utf-8
#func : create prefix list
#系统中adge的生成是用这个脚本生成的。


import datetime
import os, sys
import requests
import json

#from . import log_date
#from . import all_defined_api

from log_date import Logger, d_date
from all_defined_api import pg_exec


#logs = log_date.Logger()
logs = Logger()

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)         #把备案脚本的目录放到环境变量中去



def create_database_table():
    logs.info("{create_base()/postgre sql [service_list] } processing......")

    #创建表, log_date.d_date
    create_str = "CREATE TABLE service_list_" + d_date + \
        "(service_id INT PRIMARY KEY,service_name VARCHAR(20)) TABLESPACE cdnetworks_beian;"

    create_str = "CREATE TABLE time_list_" + d_date + "(time VARCHAR(20)) TABLESPACE cdnetworks_beian"
    #all_defined_api.pg_exec(create_str)
    pg_exec(create_str)

    logs.info("{create_base()} ended......")


def get_service_info():
    from conf.oui_api_info import service_name
    from all_defined_api import post_api_request, pg_exec_values

    logs.info(">>>>>> [ import_service_list ] <<<<<<   processing......")

    post_data = {'offline' : 0}
    res = post_api_request(service_name, post_data)

    service_values = []
    if res['status_code'] == 200:
        for line in res['data']:
            service_values.append((str(line['id']).strip(' \t\n\r'), str(line['dns_prefix']).strip(' \t\n\r')))

        insert_pg_command = "INSERT INTO service_list_" + d_date + "(service_id, service_name) VALUES (%s, %s)"
        pg_exec_values(insert_pg_command,service_values)

        logs.info(">>>>>> [ import_service_list ] <<<<<<   ended.......")

    else:
        logs.exception("!!!!!! [ import_service_list ] !!!!!!   failed.......")
        raise Exception

if __name__ == '__main__':
    create_database_table()
    #get_service_info()
