import json
from ..models import *
import pandas as pd
import math
from .nusmodsparser import *

# Convert a list of tuples into a JSON Format for HTTP Response
def tuple_parser(tup_list):
    json_array = []
    for rank in range(1, len(tup_list) + 1):
        json_dict = {}
        json_dict["rank"] = rank
        json_dict["start"] = (tup_list[rank - 1])[0]
        json_dict["end"] = json_dict["start"] + 1
        json_dict["day"] = (tup_list[rank - 1])[1]
        json_obj = json.dumps(json_dict)
        json_array.append(json_obj)
    return json_array

# Get traffic Dataframe for appropriate Gym
def get_gym_traffic(gym_name : str):
    if gym_name == 'UTown':
        return pd.DataFrame(list(UTTraffic.objects.all().values()))
    elif gym_name == 'USC':
        return pd.DataFrame(list(USCTraffic.objects.all().values()))
    else:
        return pd.DataFrame(list(MPSHTraffic.objects.all().values()))

# Get timeslots in ascending order of traffic
def get_gym_timeslots(gym_traffic_df : pd.DataFrame, reads : pd.DataFrame, username : str):
    gym_traffic_df.set_index('hour', inplace= True)
    reads.set_index('hour', inplace= True)
    # link = request.GET.get('modslink')
    link = UserSettings.objects.filter(username = username)
    print(type(link))
    link = 'https://nusmods.com/timetable/sem-2/share?CP2201=LEC:1&CS1101S=LEC:1,TUT:04,REC:01&CS1231S=TUT:05,LEC:1&CS2100=LEC:1,LAB:20,TUT:07&CS2102=TUT:16,LEC:1&CS2103=TUT:01,LEC:1'
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    avg_traffic_dict = {}
    for day in days:
        for h in range(7, 22):
            avg_traffic = math.floor(gym_traffic_df.loc[h, day] / reads.loc[h, day]) if reads.loc[h, day] != 0 else 0
            if avg_traffic in avg_traffic_dict:
                avg_traffic_dict[avg_traffic].append(tuple([h, day]))
            else:
                avg_traffic_dict[avg_traffic] = []
                avg_traffic_dict[avg_traffic].append(tuple([h, day]))
    traffics = list(avg_traffic_dict.keys())
    traffics.sort()
    timeslot_list = []
    for traffic in traffics:
        if(traffic != 0):
            timeslot_list += avg_traffic_dict[traffic]
    student_timetable = get_student_timetable(link)
    filtered_timeslot_list = []
    for timeslot in timeslot_list:
        if timeslot[1] in student_timetable and timeslot[0] in student_timetable[timeslot[1]]:
            continue
        else:
            filtered_timeslot_list.append(timeslot)
    return tuple_parser(filtered_timeslot_list)
