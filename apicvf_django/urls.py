"""apicvf_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

# ADDED BY METWORK/MFSERV/DJANGO PLUGIN TEMPLATE
# FOR CONFIGURING hello app
from django.conf.urls import include, url

urlpatterns.append(url(r'^procedere/', include('procedere.urls')))

urlpatterns.append(url(r'^epistola/', include('epistola.urls')))
urlpatterns.append(path('', include('epistola.urls')))


# ADDED BY METWORK/MFSERV/DJANGO PLUGIN TEMPLATE
# TO PROVIDE PREFIX BASED ROUTING
PREFIXES = [r"^apicvf_django/"]
urlpatterns = [url(x, include(urlpatterns)) for x in PREFIXES]
