from django.test import Client
# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gymtym.settings')


# Test 1 = PUT request to update User Settings
username = 'myre'
modslink = 'https://nusmods.com/timetable/sem-2/share?CP2201=LEC:1&CS1101S=LEC:1,TUT:04,REC:01&CS1231S=TUT:05,LEC:1&CS2100=LEC:1,LAB:20,TUT:07&CS2102=TUT:16,LEC:1&CS2103=TUT:01,LEC:1'
days = 'Monday,Tuesday,Wednesday,Thursday'
day_time = 'Afternoon,Evening'
gym_name = 'USC'

client = Client()
response = client.post('/timeslots/usersettings/', {'username' : username, 'modslink' : modslink, 
                                                    'days' : days, 'day_time' : day_time, 'gym_name' : gym_name})

print("Status: " + str(response.status_code))

# client.get('/timeslots/usersettings/')


