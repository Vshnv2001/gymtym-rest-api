from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    # path('', views.index, name='index'),
    path('gymtyms/', views.to_df, name= 'To df'), 
    path('usersettings/', views.user_settings, name= 'User Settings'),
]