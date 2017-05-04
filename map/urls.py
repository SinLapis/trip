from django.conf.urls import url
from . import views
from django.views.static import serve

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^generate/$', views.generate_route, name='generate'),
    url(r'^show/$', views.show_attractions, name='show'),
    url(r'^full/(?P<path>.*)', serve,
        {'document_root': '/usr/local/project/trip/full'}
        ),
    url(r'^detail/$', views.show_detail, name='detail'),
]
