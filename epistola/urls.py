from django.urls import path
from epistola import views

urlpatterns = [
    path('', views.index, name='index'),
]