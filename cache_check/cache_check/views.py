from django.shortcuts import render
from django.shortcuts import HttpResponse, render, redirect




def tools(request):
    if request.method == 'GET':
        return render(request, 'tools.html')

def querycustomer(request):
    if request.method == 'GET':
        return render(request, 'querycustomer.html')
    
    if request.method == 'POST':
        print(request.method)
        api_url = 'https://pantherapi.cdnetworks.com/rest/int/api@cdnetworks.com:cd3n3tw0rks/get_service_info/'
        post_data = {'type':'customer'}
        customer_name = request.POST.get('customer_name')
        post_data['name'] = customer_name.strip()
    
        import requests, json
        r = requests.post(api_url, data = post_data)
        res = json.loads(r.text)
        if res['status_code'] == 200:
            return HttpResponse(json.dumps(res['data'])) 
