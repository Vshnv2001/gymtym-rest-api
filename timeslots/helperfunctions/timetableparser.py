import json
from ..models import *
import pandas as pd
import math
from .nusmodsparser import *

# Get five timeslots for each day
def get_best_timeslots(avg_traffic_dict):
    for day in avg_traffic_dict.keys():
        if (len(avg_traffic_dict[day])) > 5:
            avg_traffic_dict[day] = (avg_traffic_dict[day])[0 : 5]
    return avg_traffic_dict

# Add Day time to timetable
def day_time_in_timetable(timetable_dict : dict, busy_time : list, day_list : list):
    for day in day_list:
        if day in timetable_dict.keys(): 
            timetable_dict[day] += busy_time
        else:
            timetable_dict[day] = busy_time
    return timetable_dict

# Get the time of the day to gym
def day_time_constraint(day_time : str, timetable_dict : dict, day_list : list):
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
        timetable_dict = day_time_in_timetable(timetable_dict, busy_time, day_list)
        return timetable_dict
        
# Apply constraint for days
def days_constraint(days: str, day_set : set):
    if days == 'All':
        return day_set
    else:
        return [day[0:3].lower() for day in days.split(',')]

# Get traffic Dataframe for appropriate Gym
def get_gym_traffic(gym_name : str):
    if gym_name == 'UTown' or gym_name == 'None':
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
    
    avg_traffic_dict = dict()
    for day in days:
        # Storing the average traffic for each day
        day_traffic_dict = dict()
        for h in range(7, 22):
            # Calculate the average traffic for the timeslot and day
            avg_traffic = math.floor(gym_traffic_df.loc[h, day] / reads.loc[h, day]) if reads.loc[h, day] != 0 else 0
            # If another timeslot has same avg traffic group them together in a list
            if avg_traffic in day_traffic_dict:
                day_traffic_dict[avg_traffic].append(h)
            else:
                day_traffic_dict[avg_traffic] = []
                day_traffic_dict[avg_traffic].append(h)
        # Get all the keys (traffic values) into a list for sorting
        traffics = list(day_traffic_dict.keys())
        traffics.sort() 
        day_timeslot_list = [] # Stores timeslots in ascending order of traffic
        for traffic in traffics:
            day_timeslot_list += day_traffic_dict[traffic]
        avg_traffic_dict[day] = day_timeslot_list

    # Get Student timetable in {day : set(hours)} format
    student_timetable = get_student_timetable(link)
    student_timetable = day_time_constraint(day_time, student_timetable, days)
 
    allowed_days = days_constraint(days_lst, set(days))

    for day in list(avg_traffic_dict.keys()):
        if day not in allowed_days:
            del avg_traffic_dict[day]
        else:
            if day in student_timetable.keys():
                for timeslot in student_timetable[day]:
                    if timeslot in avg_traffic_dict[day]:
                        avg_traffic_dict[day].remove(timeslot)
            avg_traffic_dict[day] = list(avg_traffic_dict[day])
    avg_traffic_dict = get_best_timeslots(avg_traffic_dict)
    return json.dumps(avg_traffic_dict)


