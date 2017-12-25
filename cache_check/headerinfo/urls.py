from django.conf.urls import url
from . import  views


urlpatterns = [
    url(r'^index.html', views.index),
    url(r'^get_ip_list/', views.get_ip_list),
    url(r'^table_ip_list/', views.table_ip_list),
    url(r'^get_headers_md5/', views.get_headers_md5),
    url(r'^table_header_list/', views.get_headers_md5),
]
