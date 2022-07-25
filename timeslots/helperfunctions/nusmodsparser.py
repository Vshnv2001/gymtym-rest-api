import requests
import datetime
import json
import math
from django.http import HttpRequest

def link_to_modules(link : str, sem : int):
    link = link.split('?')[1]
    mods = link.split('&')
    mods_dict = {}
    for mod in mods:
        mod_split = mod.split('=')
        timeslot_dict = {}
        timeslots = mod_split[1].split(',')
        for timeslot in timeslots:
            timeslot_split = timeslot.split(':')
            if timeslot_split != '':
                timeslot_dict[timeslot_split[0]] = timeslot_split[1]
            else:
                timeslot_dict = {}
        mods_dict[mod_split[0]] = timeslot_dict
    return mods_dict

def get_acad_year():
    this_year = datetime.datetime.today().year
    if datetime.datetime.today().month < 6: this_year -= 1
    next_year = this_year + 1
    return str(this_year) + "-" + str(next_year)
get_acad_year()

def get_module_timetable(moduleCode : str, acadYear : str, sem : int):
    get_request = "https://api.nusmods.com/v2/{acadYear}/modules/{moduleCode}.json"
    get_request = get_request.format(acadYear = acadYear, moduleCode = moduleCode)
    response = requests.request('GET', get_request)
    response = json.loads(response.content.decode('utf-8'))
    sem = 0 if len((response['semesterData'])) == 1 else sem - 1
    timetable = (((response['semesterData'])[sem])['timetable'])
    return timetable


def mapping(class_type : str):
    return {
        "LEC" : "Lecture", 
        "TUT" : "Tutorial",
        "LAB" : "Laboratory", 
        "REC" : "Recitation"
    }.get(class_type, '')

def get_timeslot(class_list : list, class_type : str, class_id : str) -> dict:
    class_type = mapping(class_type)
    for class_obj in class_list:
        if class_id in class_obj['classNo'] and class_type == class_obj['lessonType']:
            return class_obj
        
def get_student_timetable(mod_link : str) -> dict:
    if mod_link != '':
        mod_link.replace("'", "")
        sem = 1 if 'sem-1' in mod_link else 2
        mods_dict = link_to_modules(mod_link, sem)
        timetable_dict = dict()
        acad_year = get_acad_year()
        for mod_code, lessons in mods_dict.items():
            for lesson, lesson_number in lessons.items():
                class_list = get_module_timetable(mod_code, acad_year, sem)
                timeslot = get_timeslot(class_list, lesson, lesson_number)
                if timeslot == None:
                    continue
                day = ((timeslot['day'])[0 : 3]).lower()
                hours = math.ceil((int(timeslot['endTime']) - int(timeslot['startTime']))/100)
                hours_list = []
                startTime = math.floor(int(timeslot['startTime']) / 100)
                for i in range (startTime, startTime + hours):
                    hours_list.append(i)
                if day in timetable_dict:
                    timetable_dict[day] += hours_list
                else:
                    timetable_dict[day] = hours_list
        return timetable_dict
    else:
        return dict()