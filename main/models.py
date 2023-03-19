from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Visit(models.Model):
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="visit_doctor"
    )
    date = models.DateField()
    time = models.TimeField(default=datetime.time(0, 0))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visit_user")

    def __str__(self):
        return (
            str(self.doctor.first_name)
            + " "
            + str(self.doctor.last_name)
            + " "
            + str(self.user.first_name)
            + " "
            + str(self.user.last_name)
            + " "
            + str(self.date)
            + " "
            + str(self.time)
        )


class Profile(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profile_user"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    is_doctor = models.BooleanField(default=False)
    # if is doctor
    desc = models.TextField(blank=True)
    spec = models.TextField(blank=True)
    img = models.ImageField(upload_to="images/", default="images/default_picture.jpg")
    # if not
    pesel = models.IntegerField(default=0)
    tel = models.IntegerField(default=0, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=6, blank=True)
    street = models.CharField(max_length=100, blank=True)
    addr_number = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return (
            str(self.user_id)
            + " "
            + str(self.user.first_name)
            + " "
            + str(self.user.last_name)
            + " "
            + str(self.is_doctor)
        )


class Chat(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_patient"
    )
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_doctor"
    )

    def __str__(self):
        return str(self.user.id) + " " + str(self.doctor.id) + " chat"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="msg_chat")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="msg_author"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return str(self.author.id) + " " + self.text
