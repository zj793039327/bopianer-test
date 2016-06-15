from django.conf.urls import url
from . import views

app_name = 'tools'
urlpatterns = [

    url(r'^wc-jsticket', views.get_js_ticket),
    url(r'^auto-reply', views.auto_reply),

    url(r'^list', views.list),
    url(r'^score/new', views.new, name='new'),
    url(r'^score/([a-fA-F0-9]{32})/add-widget', views.add_widget, name='add-widget'),
    url(r'^index', views.index),
]
