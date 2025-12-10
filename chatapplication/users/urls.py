"""
URL configuration for chatapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path
from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('see/', views.users, name='users'),
    path('chats/', views.chats, name='chats'),
    path('completechats/', views.completechats, name='completechats'),

    path('comchats/', views.comchats, name='comchats'),
    path('log/', views.loginpage, name='login'),
    path('reg/', views.registerpage, name='registerpage'),
    path('profile/', views.profile, name='profile'),
    path('groupchat/', views.groupchat, name='groupchat'),
    path('incomplete/',views.incompletechats,name='incompletechats'),
    path('adduser/', views.adduser, name='adduser'),
   
    path("save-message/", views.save_message, name="save-message"),
   
    # API endpoints (put inside the list)
    path('api/add-complete-chat/', views.add_complete_chat, name='add-complete-chat'),
    path('api/completechats/', views.get_completechats_json, name='completechats-json'),
    path('api/save-message/', views.save_message, name='save-message'),
    path('api/messages/<int:user_id>/', views.get_user_messages, name='messages-json'),
]


