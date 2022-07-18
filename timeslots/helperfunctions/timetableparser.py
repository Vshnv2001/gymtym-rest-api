import json
import time
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

# Add Day time to timetable
def day_time_in_timetable(timetable_dict : dict, busy_time : list, day_set : set):
    for day in day_set:
        if day in timetable_dict.keys(): 
            timetable_dict[day] += set(busy_time)
        else:
            timetable_dict[day] = set(busy_time)
    return timetable_dict

# Get the time of the day to gym
def day_time_constraint(day_time : str, timetable_dict : dict, day_set : set):
    busy_time = []
    if day_time == 'All': 
        return timetable_dict
    else:
        if 'Morning' not in day_time:
            busy_time += [i for i in range(7, 11)]
        if 'Afternoon' not in day_time:
            busy_time += [i for i in range(11, 17)]
        if 'Evening' not in day_time:
            busy_time += [i for i in range(17, 22)]
        timetable_dict = day_time_in_timetable(timetable_dict, busy_time, day_set)
        return timetable_dict
        
# Apply constraint for days
def days_constraint(days: str, day_set : set):
    if days == 'All':
        return day_set
    else:
        return set(days.split(','))

# Get traffic Dataframe for appropriate Gym
def get_gym_traffic(gym_name : str):
    if gym_name == 'UTown':
        return pd.DataFrame(list(UTTraffic.objects.all().values()))
    elif gym_name == 'USC':
        return pd.DataFrame(list(USCTraffic.objects.all().values()))
    else:
        return pd.DataFrame(list(MPSHTraffic.objects.all().values()))

# Get timeslots in ascending order of traffic
def get_gym_timeslots(gym_traffic_df : pd.DataFrame, reads : pd.DataFrame, modslink : str, days_lst : str, day_time: str):
    gym_traffic_df.set_index('hour', inplace= True)
    reads.set_index('hour', inplace= True)
    link = modslink
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
    student_timetable = day_time_constraint(day_time, student_timetable, set(days))
 
    allowed_days = days_constraint(days_lst, set(days))
    filtered_timeslot_list = []
    for timeslot in timeslot_list:
        if timeslot[1] not in allowed_days or timeslot[1] in student_timetable and timeslot[0] in student_timetable[timeslot[1]]:
            continue
        else:
            filtered_timeslot_list.append(timeslot)
    return tuple_parser(filtered_timeslot_list)
    # return filtered_timeslot_list


