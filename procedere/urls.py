from django.urls import path
from procedere import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cdp', views.cdp, name='cdp'),
]
