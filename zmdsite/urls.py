from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check/', views.check_station, name='check'),
    path('check-ftp1/', views.check_station_ftp1, name='check-ftp1'),
    path('request/', views.send_zip, name='test-zip-send'),
    path('stations-request/', views.station_list_answer, name='send-station-time-intervals'),
    path('data-request/', views.station_data_answer, name='send-station-time-intervals')

]

