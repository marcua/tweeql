from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('mysite.polls.views',
    (r'^$', 'index'),
    (r'^(?P<poll_id>\d+)/$', 'detail'),
    (r'^(?P<poll_id>\d+)/results/$', 'results'),
    (r'^(?P<poll_id>\d+)/vote/$', 'vote'),
    (r'^(?P<poll_id>\d+)/edit/$', 'edit'),
    (r'^(?P<poll_id>\d+)/editpole/$', 'editpole'),
    (r'^(?P<poll_id>\d+)/editpole1/$', 'editpole1'),
    (r'^addpole/$', 'addpole'),
    (r'^add/$', 'add'),
)
