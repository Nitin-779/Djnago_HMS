from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Room, Payment
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as logout_auth
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
User=get_user_model()

# HOME view
def HMS_app1_view(request):
    room = Room.objects.all()
    return render(request, 'index.html', context={"Room_list": room})

# Dynamic page rendering
def dynamic_template_view(request, template_name):
    return render(request, f'{template_name}')

def aboutus(request):
    return render(request, 'aboutus.html')

def cards_view(request):
    return render(request, 'cards.html')

def contact(request):
    return render(request, 'contact.html')

# Signup view
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
        else:
            try:
                validate_password(password)
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                messages.success(request, 'Registration successful! You can now login.')
                return redirect('login')
            except ValidationError as e:
                for error in e:
                    messages.error(request, error)
    return render(request, 'signup.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')
        user = authenticate(request, username=username, password=password)
        if user:
            if (selected_role == 'admin' and user.is_superuser) or (selected_role == 'user' and not user.is_superuser):
                login(request, user)
                return redirect('HMS_app1_view')
            else:
                messages.error(request, "Invalid role selected.")
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

# Logout
@login_required
def logout(request):
    logout_auth(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('HMS_app1_view')

# Payment view


@login_required
def payments(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')

        if not amount_str or not payment_method:
            messages.error(request, "Please fill all required fields.")
            return redirect('payments')

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError:
            messages.error(request, "Invalid amount. Please enter a valid number.")
            return redirect('payments')

        # ✅ Force user to be a real User instance
        user = User.objects.get(id=request.user.id)

        Payment.objects.create(
            user=user,
            amount=amount,
            payment_method=payment_method,
            transaction_id=get_random_string(12).upper(),
            status='Success'
        )
        messages.success(request, "Payment successful!")
        return redirect('HMS_app1_view')

    return render(request, 'payments.html')


@login_required
def admin_dashboard_view(request):
    # if request.user.is_superuser:
    #     users = User.objects.all()
    #     payments = Payment.objects.all()
    #     return render(request, 'admin_dashboard.html', {'users': users, 'payments': payments})
    # else:
    #     messages.error(request, "You do not have permission to access this page.")
    #     return redirect('HMS_app1_view')
    
    return render(request, 'admin_dashboard.html')


@login_required
def manage_users_view(request):
    users = User.objects.all()
    return render(request, 'manageUsers.html',{ 'users': users})

@login_required
def delete_user_view(request, user_id):
    user= User.objects.get(id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('manage_users')

@login_required
def manage_rooms_view(request):
    nitin=Room.objects.all()
    return render(request, 'manage_rooms.html',{"items":nitin})

@login_required
def delete_room_view(request, room_id):
    room = Room.objects.get(id=room_id)
    room.delete()
    messages.success(request, "Room deleted successfully.")
    return redirect('manage_rooms')


@login_required
def edit_room_view(request, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == 'POST':
        hostel_name = request.POST.get('hostel_name')
        rating = request.POST.get('rating')
        city = request.POST.get('city')
        image = request.FILES.get('image')

        if not hostel_name or not rating or not city:
            messages.error(request, "Please fill all required fields.")
            return redirect('edit_room_view', room_id=room_id)

        try:
            rating = float(rating)
            if rating < 0 or rating > 5:
                raise ValueError("Rating must be between 0 and 5.")
        except ValueError:
            messages.error(request, "Invalid rating. Please enter a number between 0 and 5.")
            return redirect('edit_room_view', room_id=room_id)

        room.hostel_name = hostel_name
        room.rating = rating
        room.city = city
        if image:
            room.image = image
        room.save()

        messages.success(request, "Room updated successfully!")
        return redirect('manage_rooms')

    return render(request, 'editroom.html', {'room': room})
        





@login_required
def add_rooms_view(request):
    if request.method == 'POST':
        hostel_name = request.POST.get('hostel_name')
        rating = request.POST.get('rating')
        city = request.POST.get('city')
        image = request.FILES.get('image')

        if not hostel_name or not rating or not city:
            messages.error(request, "Please fill all required fields.")
            return redirect('add_rooms_view')

        try:
            rating = float(rating)
            if rating < 0 or rating > 5:
                raise ValueError("Rating must be between 0 and 5.")
        except ValueError:
            messages.error(request, "Invalid rating. Please enter a number between 0 and 5.")
            return redirect('add_rooms_view')

        Room.objects.create(
            hostel_name=hostel_name,
            rating=rating,
            city=city,
            image=image
        )
        messages.success(request, "Room added successfully!")
        return redirect('manage_rooms')
    return render(request, 'add_rooms.html')

@login_required
def manage_payments_view(request):
    pay=Payment.objects.all()
    return render(request, 'manage_payments.html',{"items":pay})

def profile_view(request):
    user = User.objects.all()       
    return render(request, 'manageUsers/user_list.html', {'user': user})