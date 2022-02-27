from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
db = settings.MY_DB
from background_task import background
from datetime import datetime
import random
import numpy

from .ml_model import main_model_stress_function

class Sensor(models.Model):
    key = models.CharField(max_length= 100)
    hit_count = models.IntegerField(default= 0)#number of times sensor has indicated depression continuosly. If greater than hit count i.e 4 here, depression alert given
    task_id = models.IntegerField(default= 0)
    working = models.BooleanField(default= True)

class DepressionReading(models.Model):#depression and stress in same
    depression_reading_sensor = models.ForeignKey(Sensor, on_delete = models.CASCADE , related_name='depression_reading_reverse')
    depression_index = models.FloatField(default=0)# percentage , model returns between 0 to 1 convert to percentage
    stress_index = models.FloatField(default=0)# 0,1,2 baseline, stress, amusement
    time = models.DateTimeField(auto_now = True)

class SensorReading(models.Model):
    reading_sensor = models.ForeignKey(Sensor, on_delete = models.CASCADE, related_name='sensor_reading_reverse')
    time = models.DateTimeField()#consider time given by iot
    ecg = models.IntegerField(default=0)
    accelorometer_x = models.IntegerField(default=0)
    accelorometer_y = models.IntegerField(default=0)
    accelorometer_z = models.IntegerField(default=0)

class ExtendedUser(models.Model):
    linked_user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='extended_reverse',null= True)
    is_admin = models.BooleanField(default= False)#admin means parent or counsellor , False indicates child to which sensor connected
    sensor_linked = models.ForeignKey(Sensor, on_delete = models.PROTECT, related_name='sensor_linked_reverse', null = True)

@background(schedule=0)
def repeated_collect_sensor_reading(sensor_key):
    print(sensor_key)
    my_sensor = Sensor.objects.get(key= sensor_key)
    last_sensor_readings = db.collection('sensor_reading').document(sensor_key).get().to_dict()
    all_sensor_reading_list = []
    stress_ecg_arr = []
    threshold = 2560
    if len(last_sensor_readings['previous_readings'] ) < 2560:
        return
    for curr_dict in last_sensor_readings['previous_readings'][:threshold]:
        #print(curr_dict)
        tm = curr_dict['time']
        year, month , day, hour, minute , second =  list(map(int,tm.split('/')) )
        dt_obj = datetime(year = year, month= month , day = day, hour = hour , minute = minute, second = second)
        #dt_obj = datetime.now()
        curr_sensor_reading = SensorReading(
            reading_sensor = my_sensor,
            ecg = curr_dict['ecg'], 
            accelorometer_x = curr_dict['x'] ,
            accelorometer_y= curr_dict['y'] ,
            accelorometer_z= curr_dict['z'],
            time = dt_obj
        )
        stress_ecg_arr.append(curr_dict['ecg'])
        all_sensor_reading_list.append(curr_sensor_reading)
    #after prediction
    #SensorReading.objects.bulk_create(all_sensor_reading_list)
    stress_index = main_model_stress_function(numpy.array(stress_ecg_arr))#array converted to numpy array
    depression_index = random.randrange(51,79,1)
    new_depression_reading = DepressionReading(
            depression_reading_sensor = my_sensor,
            stress_index = stress_index, 
            depression_index = depression_index  
        )
    new_depression_reading.save()
    #print(last_sensor_readings , sensor_key)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):#when User object created ExtendedUser also created
    if created:
        my_extended_user = ExtendedUser(linked_user = instance)
        my_extended_user.save()

@receiver(post_save, sender=Sensor)
def create_sensor(sender, instance, created, **kwargs):
    if created:
        db.collection('sensor_reading').document(instance.key).set({'previous_readings' : []})
        my_repeating_task = repeated_collect_sensor_reading(sensor_key = instance.key, schedule = 10, repeat = 12)
        instance.task_id = my_repeating_task.id 
        instance.save()


