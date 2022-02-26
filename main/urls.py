"""calendar_class URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
app_name = 'main'

urlpatterns = [
    path('test/', views.test,name='test'),
    path('get_instantenous_data/<str:sensor_key>/', views.get_instantenous_data , name='get_instantenous_data'),
    path('get_series_data/<str:sensor_key>/<int:tot_time>/<int:delta>/', views.get_series_data, name='get_series_data'),
    path('register/', views.register, name='register'),
    path('login/<str:username>/' , views.login, name='login')
]