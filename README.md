# cache_check
运维小工具/head节点遍历/客户配置查询

V:python3
m:postgresql
django


问题：
    前端传递一个参数到后端函数中，后端的另外一个函数也想需要用这个传递过来的参数，那如何处理？
    我用的数据库来记录，还有其他方法吗？
    

every_week : 由于节点和pop都有可能随时更新，为了保证数据的准确性，每周重新通过api来获取节点、pop等的最新信息
