import datetime
import os, sys
import requests
import json
import re


# from log_date import Logger, d_date
# from all_defined_api import pg_exec, return_pg_exec



from . import log_date
from . import all_defined_api


logs = log_date.Logger()
# logs = Logger()


def get_all_ip():        #去获取vips
    logs.info('to get the IP LIST !!!')
    # command_select_service = "select service_name from select_service;"
    # res = all_defined_api.return_pg_exec(command_select_service)
    # service_name = "".join(res[0])
    #这里只用一张表来做实验，后面的  service_name 与 data_time 统一入库
    #service_name = "CL1"

    #在数据库中获取需要查询的service组
    command_select_service = "select * from select_service  order by  service_name  desc limit 1;"
    res = all_defined_api.return_pg_exec(command_select_service)
    service_name = "".join(res[0])

    #在数据库中获取各个api表最新更新的表
    command_select_date = "select * from time_list_20171211  order by  time  desc limit 1;"
    res = all_defined_api.return_pg_exec(command_select_date)
    choose_date = "".join(res[0])
    print('----------------------------------------',service_name, choose_date)

    command_get_vips = "select vips from get_band_vip_" + choose_date + "_" +service_name + " as A inner join " \
                       "service_with_node_" + choose_date + "_" +service_name + " as B on A.node_name = B.node_name"

    print('取ip_list的命令', command_get_vips)

    res = all_defined_api.return_pg_exec(command_get_vips)

    return res


def request_header(post_data):
    '''
    传入前段发来的表单数据，然后对平台下的ip做head请求，每个ip一个字典，放到字典当中
    目前的request的https代理访问有问题，所以现在无论是https还是http都是走得http
    '''
    service_name = post_data['service_id']    
    from . import all_defined_api

    try:
        drop_select_service_command = 'drop table select_service;'
        all_defined_api.pg_exec(drop_select_service_command)
    except Exception as e:
        print('drop  select_service table Error:', e)

    create_str = "CREATE TABLE select_service (service_name VARCHAR(64)) TABLESPACE cdnetworks_beian;"
    all_defined_api.pg_exec(create_str)
    logs.info("{create_[select_service_]  } for get files info ended......")

    service_name_ruku = [(service_name, )]
    command_insert_service = "INSERT INTO select_service (service_name) VALUES (%s);"
    all_defined_api.pg_exec_values(command_insert_service, service_name_ruku)
    

    ip_list = get_all_ip()
    s = requests.session()
    header = {
        'User-Agent': 'curl/7.54.0',
        'Accept': '* / *',
        'Proxy-Connection': 'Keep-Alive'
    }
    if post_data['cache_header'] == 'on':
        header['x-cache-test'] = 'flush'

    get_all_headers = []
    # post_data = {'service_id': '25', 'check_url': 'vp1.stu.126.net/crossdomain.xml', 'check_method': 'GET', 'check_origin': '',
    #             'cache_header': None}
    n = 1
    #url分三种情况，https,http, www, 开头的三种情况
    if re.match('https', post_data['check_url']):
        for single_ip in ip_list:
            single_ip = ''.join(single_ip)
            replace_https = re.compile('https')
            url = replace_https.sub('http', post_data['check_url'])
            proxie = {}
            proxie['http'] = 'http://' + single_ip + ':80'
            print( [n] ,'--', single_ip)
            n += 1

            try:
                r = s.head(url,headers= header,proxies=proxie,verify=False,timeout=10)
                reponse = r.headers
            except Exception as e:
                reponse = {'error':'NODATA'}
                reponse['edge_Ip'] = single_ip
                get_all_headers.append(reponse)
                continue

            reponse['edge_Ip'] = single_ip
            reponse['status_code'] = r.status_code
            get_all_headers.append(reponse)

    elif re.match('http', post_data['check_url']):
        for single_ip in ip_list:
            single_ip = ''.join(single_ip)
            url = post_data['check_url']

            proxie = {}
            proxie['http'] = 'http://' + single_ip + ':80'
            print( [n] ,'--', single_ip)
            n += 1
            try:
                r = s.head(url, headers=header, proxies=proxie, verify=False, timeout=10)
                reponse = r.headers
            except Exception as e:
                reponse = {'error':'NODATA'}
                reponse['edge_Ip'] = single_ip
                get_all_headers.append(reponse)
                continue

            reponse['edge_Ip'] = single_ip
            reponse['status_code'] = r.status_code
            get_all_headers.append(reponse)

    else:
        url = 'http://' + post_data['check_url']
        for single_ip in ip_list:
            single_ip = ''.join(single_ip)

            proxie = {}
            proxie['http'] = 'http://' + single_ip + ':80'
            print( [n] ,'--', single_ip, 'get_header_info')
            n += 1
            try:
                r = s.head(url, headers=header, proxies=proxie, verify=False, timeout=3)
                reponse = r.headers
            except Exception as e:
                reponse = {'error':'NODATA'}
                reponse['edge_Ip'] = single_ip
                get_all_headers.append(reponse)
                continue

            reponse['edge_Ip'] = single_ip
            reponse['status_code'] = r.status_code
            get_all_headers.append(reponse)

    # for line in get_all_headers:
    #     print(line)

    return get_all_headers




def return_res(post_data):
    #post_data = {'service_id': '25', 'check_url': 'vp1.stu.126.net/crossdomain.xml', 'check_method': 'HEAD', 'check_origin': '1.1.1', 'cache_header': None}
    origin_edge_data = {}
    if post_data['check_method'] == 'HEAD':
        if re.match('https', post_data['check_url']):
            replace_https = re.compile('https')
            url = replace_https.sub('http', post_data['check_url'])
        elif re.match('http', post_data['check_url']):
            url = post_data['check_url']
        else:
            url = 'http://' + post_data['check_url']

        s = requests.session()
        proxie = {}
        if post_data['check_origin']:
            proxie['http'] = 'http://' + post_data['check_origin'] + ':80'
            header = {
                'User-Agent': 'curl/7.54.0',
                'Accept': '* / *',
                'Proxy-Connection': 'Keep-Alive'
            }
            print(proxie)
            try:
                r = s.head(url, proxies=proxie, verify=False, timeout=3)
                print('=======================================================',r)
                reponse = r.headers
                status_code = r.status_code
                reponse['Origin_Ip'] = post_data['check_origin']
            except Exception as e:
                reponse = {'error' : 'NODATA'}
                reponse['notice'] = 'Check_origin'
                reponse['Origin_Ip'] = post_data['check_origin']
                reponse['status_code'] = '50x' 
                print('源站有问题.............')
        else:
            reponse = {'Origin' : 'NO'}

        print('reponse',reponse)
        origin_edge_data['origin'] = reponse

        res = request_header(post_data)
        origin_edge_data['edge'] = res

        return origin_edge_data
    else:
        print('have origin, and get')     #get下载md5验证





def test():
    s = requests.session()
    proxie = {
        #'http': 'http://14.0.58.97:80',
        'https': 'https://14.0.58.97:443',
    }
    header = {
        'User-Agent': 'curl/7.54.0',
        #'Accept': '* / *',
        'Proxy-Connection': 'Keep-Alive',
        'x-cache-test': 'flush'
    }
    url = 'https://vp1.stu.126.net/crossdomain.xml'


    reponse = s.get(url,headers=header, proxies=proxie).headers

    print(reponse)



if __name__ == "__main__":
    #get_all_ip()
    #test()
    #request_header()
    res = return_res()
    print(res)
