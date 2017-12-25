

usename_pw = '

#=========【1】=========
#offline=0    去除 offline和broken的机器,通过band api查询ip时，没有判断offline的参数，需要结合这个表

node_list = 'https://pantherapi.cdnetworks.com/rest/int/' + usename_pw +'/node/list/'

#============【2】==================
#这个获取的band包括offline的，需要注意下
#可以获取都某个dns_prefix下面有多少band,(band_id)

edge_info = 'https://pantherapi.cdnetworks.com/rest/int/' + usename_pw + '/get_edge_info/'


#可以知道这个band下面配置了哪些vip，从何得到对应prefix下面有哪些ip
band_vip = 'https://pantherapi.cdnetworks.com/rest/int/' + usename_pw + '/get_band_vip/'


#【1】与【2】 量表联合查询排除掉offline的机器




#========[3]===========
#获取prefix

service_name = 'https://pantherapi.cdnetworks.com/rest/int/' + usename_pw + '/service/list/'


#========[4]============
#postgrep connect info
db_conn_str = "host=127.0.0.1 port=5432 dbname=cdnetworks_beian user=cdnetworks_beian password=cdnetworks_beian"
