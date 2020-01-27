from django.urls import path
from apicvf import views

urlpatterns = [
    path('', views.index, name='index'),
    path('testCdP', views.TestView.as_view()),
    path('testInject', views.Injecting.as_view())
]
