from tracemalloc import start
from django.shortcuts import render
from .models import *
from django.http import HttpRequest, HttpResponse, QueryDict
from . import tests
import time
from ast import literal_eval

from .helperfunctions.timetableparser import *
import pandas as pd
from rest_framework.decorators import api_view


@api_view(['POST', 'PUT'])
def user_settings(request : HttpRequest):
    print(type(request.body))
    # print(request.POST.get('username'))
    # request.POST.get = QueryDict(request.body)
    username = request.POST.get('username')
    modslink = request.POST.get('modslink')
    gym_name = request.POST.get('gym_name')
    days = request.POST.get('days')
    day_time = request.POST.get('day_time')
    print("User: " + username)
    if UserSettings.objects.filter(username = username).exists():
        user_row : UserSettings
        user_row = UserSettings.objects.get(username = username)
        user_row.mods_link = modslink
        user_row.days = days
        user_row.gym_name = gym_name
        user_row.day_time = day_time
    else:
        user_row = UserSettings(username = username, mods_link = modslink, days = days, day_time = day_time)
    user_row.save()
    return HttpResponse(status=200)
 

@api_view(['GET'])
def to_df(request: HttpRequest):
    start = time.time()
    gym_name = request.GET.get('gym')
    user_name = request.GET.get('user')
    gym_traffic_df = get_gym_traffic(gym_name)
    reads = pd.DataFrame(list(NumberOfReadings.objects.all().values()))
    modslink = pd.DataFrame(list(UserSettings.objects.filter(username = user_name).all().values())).loc[0, "mods_link"]
    days = pd.DataFrame(list(UserSettings.objects.filter(username = user_name).all().values())).loc[0, "days"]
    day_time = pd.DataFrame(list(UserSettings.objects.filter(username = user_name).all().values())).loc[0, "day_time"]
    timeslots = get_gym_timeslots(gym_traffic_df, reads, modslink, days, day_time)
    end = time.time()
    print(end - start)
    return HttpResponse(timeslots)
        
    
    
    



