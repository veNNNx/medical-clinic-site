from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length = 100)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.title 

class Visit(models.Model):
    doctor = models.IntegerField()
    date = models.DateField()
    time = models.TimeField(default=datetime.time(0,0))
    user_id = models.TextField()

    def __str__(self):
        return str(self.doctor) + ' ' + str(self.date) + ' ' + str(self.time)

class Profile(models.Model):
    user_id = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add = True)
    date_modified = models.DateTimeField(auto_now_add = True)
    is_doctor = models.BooleanField(default = False)
    # if is doctor
    desc = models.TextField(blank=True)
    spec = models.TextField(blank=True)
    img = models.ImageField(upload_to='images/', default='images/default_picture.jpg')
    # if not
    pesel = models.IntegerField(default = 0)
    tel = models.IntegerField(default = 0, blank=True)
    city = models.CharField(max_length = 100, blank=True)
    zip_code = models.CharField(max_length = 6, blank=True)
    street = models.CharField(max_length = 100, blank=True)
    addr_number = models.CharField(max_length = 100, blank=True)
    

    def __str__(self):
        return str(self.user_id) + ' ' + str(self.is_doctor)
