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
    url(r'^static/(?P<path>.*)', serve,
        {'document_root': '/usr/local/project/trip/map/templates/map/static'}),
    url(r'^detail/$', views.show_detail, name='detail'),
    url(r'^top-tags/$', views.show_tags, name='top-tags'),
    url(r'^route/$', views.show_route, name='route'),
    url(r'^route-detail/$', views.route_detail, name='route-detail')
]
