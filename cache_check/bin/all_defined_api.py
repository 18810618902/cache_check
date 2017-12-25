#/usr/bin/env python3
#coding:utf-8
#func : create prefix list

import psycopg2
import sys, os
import requests
import json



root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)         #把备案脚本的目录放到环境变量中去

from conf.oui_api_info import db_conn_str


def pg_exec(exec_str):
    conn = psycopg2.connect(db_conn_str)
    cur = conn.cursor()
    cur.execute(exec_str)
    conn.commit()

    cur.close()
    conn.close()

def post_api_request(api_url,post_data):
    r = requests.post(api_url, data = post_data)
    #print(r.text)
    res = json.loads(r.text)
    return res


def pg_exec_values(exec_str, command_values):
    conn = psycopg2.connect(db_conn_str)
    cur = conn.cursor()
    cur.executemany(exec_str, command_values)       #可传递多个value，一起操作
    conn.commit()

    cur.close()
    conn.close()


def return_pg_exec(exec_str, query = None):
    conn = psycopg2.connect(db_conn_str)
    cur = conn.cursor()
    cur.execute(exec_str, query)
    res =cur.fetchall()
    conn.commit()

    cur.close()
    conn.close()
    return res