from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import message
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from shop.models import Product
# from vendor.forms import VendorForm
from .forms import  UserForm , CustomPasswordChangeForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import update_session_auth_hash
from .models import User, UserProfile

from django.contrib import messages, auth
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from vendor.models import Vendor
from orders.models import Order
import datetime

@login_required(login_url='account:login')
def myAccount(request):
    user = request.user
    if user.is_authenticated:
        redirect_url = detectUser(user)
        if redirect_url:
            return redirect(redirect_url)
        else:
            messages.error(request, 'Unable to determine dashboard for the user.')
            return redirect('account:login')
    else:
        messages.error(request, 'You need to log in to access your account.')
        return redirect('account:login')
    

# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.is_active = True
            user.save()

            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('registerUser')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'account/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name,username=username, email=email, password=password)
            user.role = User.VENDOR
            user.is_active = True
            user.save()

            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('login')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'account/registerVendor.html', context)



def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated.')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')
        

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None and user.is_active:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'account/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')




def custDashboard(request):

    product = Product.objects.all()

    context = {
        "product" : product 
    }
    return render(request, 'account/custDashboard.html' , context)


def vendorDashboard(request):
    return render(request, 'account/vendorDashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset Your Password'
            email_template = 'account/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'account/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'account/reset_password.html')


@login_required
def user_change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session
            messages.success(
                request, 'Your password was successfully updated!')
            logout(request)  # Log out the user
            return redirect('account:custDashboard')
    else:
        # Pass user=request.user to initialize the form with the user's data
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'account/change_password.html', {'form': form})