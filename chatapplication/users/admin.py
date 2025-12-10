from django.contrib import admin
from .models import Adduser, Completechats, Chats ,Login , Registration ,Profile
# Register your models here

admin.site.register(Adduser)
admin.site.register(Chats)
admin.site.register(Completechats)
admin.site.register(Login)
admin.site.register(Registration)
admin.site.register(Profile)
