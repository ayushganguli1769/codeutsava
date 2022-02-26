from background_task import background
from django.contrib.auth.models import User
#from .models import *
from django.apps import apps
apps.get_model('main.Sensor')
apps.get_model('main.SensorReading')

@background(schedule=0)
def repeated_collect_sensor_reading(sensor_key):
    pass
    """
    my_sensor = Sensor.objects.get(id=1)
    new_reading = SensorReading(reading_sensor = my_sensor)
    new_reading.save()
    """