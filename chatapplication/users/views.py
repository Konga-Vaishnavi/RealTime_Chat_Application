
from .models import Login, Registration, Profile
from .models import Chats, Completechats, Adduser , ChatMessage
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


def users(request):
    return HttpResponse("Users Home Page")

from django.shortcuts import get_object_or_404, redirect

def chats(request):
    user_id = request.session.get('user_id')
    if not user_id:
        # Create a default user for testing
        default_user = Adduser.objects.first()
        if not default_user:
            return redirect('adduser')
        request.session['user_id'] = default_user.id
        user_id = default_user.id

    try:
        sender = Adduser.objects.get(id=user_id)
    except Adduser.DoesNotExist:
        return redirect('adduser')

    receiver_id = request.GET.get('receiver_id')
    if not receiver_id:
        # Get first available user as receiver
        receiver = Adduser.objects.exclude(id=sender.id).first()
        if not receiver:
            receiver = sender  # fallback to self
    else:
        receiver = get_object_or_404(Adduser, id=receiver_id)

    # Get messages for the current user
    user_chats = Chats.objects.filter(username=sender).order_by('timestamp')

    return render(request, "chats.html", {
        "sender": sender,
        "receiver": receiver,
        "username": receiver.username,
        "user_id": sender.id,
        "user_chats": user_chats
    })
    
def completechats(request):
    # Get the user id from session
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    try:
        current_user = Adduser.objects.get(id=user_id)
    except Adduser.DoesNotExist:
        return redirect('login')

    # Get all other users
    users = Adduser.objects.exclude(id=current_user.id)

    return render(request, "completechats.html", {
        "users": users
    })




def comchats(request):
    complete_chats = Completechats.objects.all().select_related('username')
    return render(request, 'completechats.html', {'complete_chats': complete_chats})

def adduser(request):
    if request.method == 'POST':
        username = request.POST.get('newusername', '').strip()
        
        # Validate username
        if not username:
            all_users = Adduser.objects.all()
            return render(request, 'adduser.html', {
                'error': 'Username is required',
                'users': all_users,
                'total_users': all_users.count()
            })
        
        try:
            # Check if username already exists
            if Adduser.objects.filter(username=username).exists():
                all_users = Adduser.objects.all()
                return render(request, 'adduser.html', {
                    'error': f'Username "{username}" already exists',
                    'users': all_users,
                    'total_users': all_users.count()
                })
            
            # Save new user to Adduser model (username only)
            new_user = Adduser.objects.create(username=username)
            
            # IMPORTANT: Also create entry in Completechats
            Completechats.objects.create(username=new_user)

            request.session['user_id'] = new_user.id
            
            return redirect('completechats')  # Redirect after successful save
        
            
        except Exception as e:
            error_message = f"Error saving user: {str(e)}"
            all_users = Adduser.objects.all()
            return render(request, 'completechats.html', {
                'error': error_message,
                'users': all_users,
                'total_users': all_users.count()
            })
    
    
    # GET request - show all users
    all_users = Adduser.objects.all()
    context = {
        'users': all_users,
        'total_users': all_users.count()
    }
    return render(request, 'adduser.html', context)
 


# API endpoints for AJAX requests
def add_complete_chat(request):
    """API endpoint to add a chat entry to Completechats"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            # Get user
            user = Adduser.objects.get(id=user_id)
            
            # Create complete chat entry (username only)
            chat = Completechats.objects.create(username=user)
            
            return JsonResponse({
                'success': True,
                'message': 'Chat created successfully',
                'chat_id': chat.id
            })
            
        except Adduser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_completechats_json(request):
    """API endpoint to get all complete chats as JSON"""
    chats = Completechats.objects.select_related('username').values(
        'id', 'username__id', 'username__username', 'timestamp'
    )
    return JsonResponse(list(chats), safe=False, default=str)


def get_user_messages(request, user_id):
    """Return all messages for a given user as JSON"""
    try:
        msgs = Chats.objects.filter(username_id=user_id).order_by('timestamp').values('id', 'content', 'timestamp')
        # Convert queryset to list and stringify datetimes
        result = []
        for m in msgs:
            result.append({
                'id': m['id'],
                'content': m['content'],
                'timestamp': m['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if m['timestamp'] else None
            })
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
from django.http import JsonResponse
from .models import Chats

def save_message(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=405)

    user_id = request.POST.get("user_id")
    content = request.POST.get("content")

    if not user_id or not content:
        return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

    try:
        user = Adduser.objects.get(id=user_id)
    except Adduser.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    chat = Chats.objects.create(username=user, content=content)

    return JsonResponse({
        "status": "saved",
        "id": chat.id,
        "content": chat.content,
        "time": timezone.localtime(chat.timestamp).strftime('%I:%M %p')
    })

def chat_view(request):
    user_id = request.user.id
    receiver_id = request.GET.get('user_id')  # Or however you determine the chat partner
    username = None
    if receiver_id:
        # fetch username of chat partner
        user_obj = User.objects.filter(id=receiver_id).first() # type: ignore
        username = user_obj.username if user_obj else None
    
    # Pass to template context
    context = {
        'user_id': user_id,
        'receiver_id': receiver_id,
        'username': username,
        # plus other data like user_chats...
    }
    return render(request, 'chats.html', context)

def loginpage(request):
    if request.method == "POST":
        uname = request.POST['username']
        pwd = request.POST['password']
        try:
            log = Registration.objects.get(email=uname, password=pwd)

            # find matching Adduser
            chat_user = Adduser.objects.get(username=log.username)

            # store Adduser id
            request.session['user_id'] = chat_user.id

            return redirect('completechats')

        except (Registration.DoesNotExist, Adduser.DoesNotExist):
            return render(request, 'login.html', {"error": "Invalid credentials"})

    return render(request, 'login.html')

def registerpage(request):
    if request.method == "POST":
        
        fname = request.POST['first_name']
        lname = request.POST['last_name']
        email = request.POST['email']
        pwd = request.POST['password']
        cpwd = request.POST['confirm_password']
        phone = request.POST['phone_number']
        gender = request.POST['gender']
        dob = request.POST['dob']
        conditions = request.POST.get('conditions_checkbox') == 'on'
        
        # Create instance
        regi = Registration(
            first_name=fname, 
            last_name=lname, 
            email=email, 
            password=pwd, 
            confirm_password=cpwd, 
            phone_number=phone, 
            gender=gender, 
            dob=dob, 
            conditions_checkbox=conditions
        )
        regi.save()  # Save to DB

        # Use `regi` here, not `user`
        request.session['user_id'] = regi.id
        request.session['is_new_user'] = True 
        request.session["profile_username"] = fname
        request.session["profile_email"] = email
        request.session["profile_password"] = pwd
        
        return redirect('incompletechats')

    return render(request, 'registration.html')

def profile(request):
    if request.method == "POST":
        try:
            fname = request.POST['first_name']
            profile_picture = request.FILES.get('profile_picture')
            dob = request.POST['dob']
            phone = request.POST['phone_number']

            from .models import profile as ProfileModel
            prof = ProfileModel(
                first_name=fname,
                profile_picture=profile_picture,
                dob=dob,
                phone_number=phone
            )
            prof.save()
        finally:
              return redirect('completechats')
    return render(request, 'profile.html') 
    
def groupchat(request):
    return render(request, 'groupchat.html')

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        chat_id = data.get("chat_id")
        message = data.get("message")

        # 1️⃣ Fetch the chat object
        try:
            chat = Completechats.objects.get(id=chat_id)
        except Completechats.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Chat not found'}, status=404)

        # 2️⃣ Save the message properly
        chat_msg = ChatMessage.objects.create(
            chat=chat,
            content=message
        )

        return JsonResponse({
            'status': 'success',
            'id': chat_msg.id,
            'content': chat_msg.content,
            'timestamp': chat_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def get_messages(request):
    last_id = int(request.GET.get('last_id', 0))

    messages = ChatMessage.objects.filter(id__gt=last_id).values(
        'id',
        'chat_id',
        'content',
        'timestamp'
    )

    return JsonResponse({'messages': list(messages)})

def incompletechats(request):
    user_id = request.session.get("user_id")
    is_new_user = request.session.get('is_new_user', False)

    if not user_id:
        return redirect('login')  # or wherever

    if is_new_user:
        messages = []  # Empty list means no chat yet
    else:
        messages = ChatMessage.objects.filter(user_id=user_id).order_by('timestamp')

    return render(request, 'completechats.html', {'messages': messages})


