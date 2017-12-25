from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, render
import os, sys
import json

# Create your views here.

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)         #把脚本的根目录放到环境变量中去

from bin.all_defined_api import return_pg_exec

def index(request):
    #service_list = {'service_name' : []}
    if request.method == "GET":
        command_str = 'select * from service_list_20171211'
        res = return_pg_exec(command_str)
        #print(res)


    return render(request, 'index.html', {'service_list':res})




def get_ip_list(request):
    from bin.final_result import data_ruku
    if request.method == 'POST':
        service = request.POST.get('service_id')
        nali = request.POST.get('nali')
        #print('service_id',service_id)
        data_ruku(service, nali)      #不用每次都建丽了，就用一个表来做实验
        res_code = {'code':'0','message':'ok'}


    #return render(request, 'index.html', {'ip_dict':ip_list})
    return  HttpResponse(json.dumps(res_code), content_type="application/json")


def table_ip_list(request):        #ajax request
    #ip_list = {'1.1.1.1': '北京', '2.2.2.2': '天津'}
    from bin.final_result import get_vips_data
    ip_list = get_vips_data()

    return render(request, 'table_ip_list.html', {'ip_list':ip_list})


def get_headers_md5(request):
    all_data = {}
    if request.method == "POST":
        all_data['check_url'] = request.POST.get('url')
        all_data['check_origin'] = request.POST.get('origin')
        all_data['service_id'] = request.POST.get('service_id')
        all_data['check_method'] = request.POST.get('method')
        all_data['cache_header'] = request.POST.get('cache_control')

    from bin.request_method import return_res
    print(all_data)
    res_dict = return_res(all_data)

    return render(request, 'table_header_list.html', {'table_header': res_dict} )
    #return HttpResponse(json.dumps('success'), content_type="application/json")

if __name__ == '__main__':
    from bin.final_result import test
    test()



























