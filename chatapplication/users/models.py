from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Login(models.Model):
    username=models.CharField(max_length=150)
    password=models.CharField(max_length=150)

class Adduser(models.Model):
    username = models.CharField(max_length=100, unique=True)

class Registration(models.Model):
    first_name=models.CharField(max_length=150)
    last_name=models.CharField(max_length=150)
    email=models.EmailField()
    password=models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    confirm_password=models.CharField(max_length=150)
    phone_number=models.CharField(max_length=15)
    gender=models.CharField(max_length=10)
    dob=models.DateField()
    conditions_checkbox=models.BooleanField()


class Profile(models.Model):
    first_name=models.CharField(max_length=150)
    profile_picture=models.ImageField(upload_to='profiles/')
    dob=models.DateField()
    phone_number=models.CharField(max_length=15)



    

    def __str__(self):
        return self.username


class Completechats(models.Model):
    # Use Adduser as ForeignKey
    username = models.ForeignKey(Adduser, on_delete=models.CASCADE)
    lastmessage = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username.username} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


class Chats(models.Model):
    username = models.ForeignKey(Adduser, on_delete=models.CASCADE)
    activity_status = models.BooleanField(default=False)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
     return f"{self.username.username} - {self.activity_status}"


class ChatMessage(models.Model):
    chat = models.ForeignKey(Completechats, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.chat} at {self.timestamp}"
   
