"""
URL configuration for disease project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path,include
from .views import home, predict,additional_symptoms,predict_result,show_precaution,blog,about

urlpatterns = [
    path('',home, name='home'),
    path('about/',about,name='about'),
    path('blog/',blog,name='blog'),
    path('predict/', predict, name='predict'),
    path('predict/extra/', additional_symptoms, name='additional_symptoms'),
    path('predict/result/', predict_result, name='predict_result'),
    path('predict/precaution/', show_precaution, name='show_precaution'),

]
