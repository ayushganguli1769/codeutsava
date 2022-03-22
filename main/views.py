from django.shortcuts import render
from django.http import HttpResponse,Http404, JsonResponse
from .repeating_tasks import repeated_collect_sensor_reading
from .models import DepressionReading,Sensor
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, views
from rest_framework import permissions
from rest_framework import authentication
from django.views.decorators.csrf import csrf_exempt

import json
import math
import datetime

def test(request):
    return HttpResponse("okkk")

@csrf_exempt
def get_instantenous_data(request,sensor_key):
    try:
        curr_sensor = Sensor.objects.get(key = sensor_key)
        last_depression_reading = curr_sensor.depression_reading_reverse.last()
        curr_time = last_depression_reading.time 
        recorded_time_string = "%d/%d/%d/%d/%d/%d"%(curr_time.year, curr_time.month, curr_time.day,curr_time.hour, curr_time.minute, curr_time.second)
        alert_bool = last_depression_reading.stress_index == 1
        return JsonResponse({
            'is_success': True,
            'recorded_time' : recorded_time_string,
            'depression_index': last_depression_reading.depression_index,
            'stress_index': last_depression_reading.stress_index,
            'alert': alert_bool,#true means child has mental problems
        }, status = 200)
    except Exception as e:
        print(e)
        return JsonResponse({
            'is_success': False,
            'error': str(e)
        }, status = 400)

@csrf_exempt
def get_series_data(request,sensor_key,tot_time,delta):#tot_time: seconds, delta: seconds
    curr_sensor = Sensor.objects.get(key = sensor_key)
    depression_readings = curr_sensor.depression_reading_reverse.order_by('-time')
    last_depression_reading = depression_readings.first()
    last_reading_time = last_depression_reading.time
    n =  math.floor(tot_time / delta)
    tot_time_delta = datetime.timedelta(tot_time)
    i = 0
    delta_time = datetime.timedelta(seconds= delta)
    ans= []
    #print(i,n)
    for curr_reading in depression_readings:
        curr_time = curr_reading.time 
        diff = last_reading_time - curr_time
        #print(last_reading_time , curr_time)
        if diff >= i * delta_time:
            curr_reading_dict = {
                'depression_index': curr_reading.depression_index,
                'stress_index' : curr_reading.stress_index,
                'time' : "%d/%d/%d/%d/%d/%d"%(curr_time.year, curr_time.month, curr_time.day,curr_time.hour, curr_time.minute, curr_time.second, ),
                'time_from_latest': diff.seconds
                }
            ans.append(curr_reading_dict)
            i += 1
        if i >= n :
            break

    return JsonResponse({
        'is_success': True,
        'data_arr': ans

    },status= 200)
        
@csrf_exempt
def login(request, username):#provides the sensor key. Not really a login
    try:
        curr_user = User.objects.get(username= username)
        if  curr_user.extended_reverse.sensor_linked is None:
            return JsonResponse({
                'is_success': False,
                'error': "No sensor linked"
            },status = 400)
        sensor_id = curr_user.extended_reverse.sensor_linked.key
        return JsonResponse({
                'is_success': True,
                'sensor_key' : sensor_id
            }, status = 200)
    except Exception as e:
        return JsonResponse({
            'is_success': False,
            'error': str(e)
        }, status = 400)
@api_view(['GET','POST'])
@csrf_exempt
def register(request):#only for admin aka parents/counsellor
    try:
        username = request.data['username']
        password1 = request.data['password1']
        password2 = request.data['password2']
        email = request.data['email']
        sensor_key = request.data['sensor_key']
        if password1 == password2:
            if User.objects.filter(username = username).exists():
                return Response({
                    'is_success': False,
                    'error': "Username already exists"
                    }, status = 400)  
            else:
                user= User.objects.create_user(username = username, password = password1)
                user.save()
                if Sensor.objects.filter(key = sensor_key).exists() is True:
                    curr_sensor = Sensor.objects.filter(key = sensor_key).first()
                    new_sensor_added = False
                else:
                    curr_sensor = Sensor(key = sensor_key)
                    curr_sensor.save()
                    new_sensor_added = True
                print(curr_sensor)
                user.extended_reverse.is_admin = True
                user.extended_reverse.sensor_linked = curr_sensor
                user.extended_reverse.save()
                return Response({
                    'is_success': True,
                    'message' : "Successfully registered",
                    'new_sensor_added' : new_sensor_added,
                    'sensor_key': sensor_key,
                }, status = 200)                       
        return Response({
            'is_success': False,
            'error': "Username already exists"
            }, status = 400)  
    except Exception as e:
        return Response({
            'is_success': False,
            'error': str(e)
        }, status = 400)
# Create your views here.
