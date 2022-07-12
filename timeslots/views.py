from django.shortcuts import render
from .models import *
from django.http import HttpRequest, HttpResponse
from . import tests
from ast import literal_eval

from .helperfunctions.timetableparser import *
import pandas as pd
from rest_framework.decorators import api_view


@api_view(['POST', 'PUT'])
def user_settings(request : HttpRequest):
    username = request.POST.get('username')
    modslink = request.POST.get('modslink')
    days = request.POST.get('days')
    day_time = request.POST.get('day_time')
    if UserSettings.objects.filter(username = username).exists():
        user_row = UserSettings.objects.get(username = username)
        user_row.mods_link = modslink
        user_row.days = days
        user_row.day_time = day_time
    else:
        user_row = UserSettings(username = username, mods_link = modslink, days = days, day_time = day_time)
    user_row.save()
    return HttpResponse(status=200)


@api_view(['GET'])
def to_df(request: HttpRequest):
    gym_name = request.GET.get('gym')
    user_name = request.GET.get('user')
    gym = get_gym_traffic(gym_name)
    reads = pd.DataFrame(list(NumberOfReadings.objects.all().values()))
    timeslots = get_gym_timeslots(gym, reads, user_name)
    return HttpResponse(timeslots)
        
    
    
    



