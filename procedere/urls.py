from django.urls import path
from procedere import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cdp', views.cdp, name='cdp'),
    path('acq', views.cdp, name='acq'),
    path('alert', views.cdp, name='alert'),
]
