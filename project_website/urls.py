"""project_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path,include,re_path
from club_admin import views

urlpatterns = [
    path('',views.index,name="index"),
    path('adminlogin/admin/',views.admin,name="admin"),
    path('super_admin/',views.super_admin,name="super_admin"),
    path('delete/', views.delete_session,name="delete_session"),
    path('adminlogin/',views.adminlog,name="adminlogin"),
    path('viewadmin/',views.viewadmin,name="viewadmin"),
    path('addadmin/',views.addadmin,name="addadmin"),
    path('addadmins/',views.addadmins,name="addadmins"),
    path('deleteadmin/',views.deleteadmin,name="deleteadmin"),
    path('deladmin/',views.deladmin,name="deladmin"),
    path('confirmdelete/',views.confirmdelete,name="confirmdelete")
]
