
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from . forms import UserProfileForm
from account.models import UserProfile
from django.contrib import messages
from orders.models import Order, ProductOrder
from account.models import User
from shop.models import Product

@login_required(login_url='login')
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        print(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        print(profile_form)
        if profile_form.is_valid() :
            profile_form.save()
            messages.success(request, 'Profile updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            
    else:
       
        profile_form = UserProfileForm(instance=profile)
        

    context = {
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'customers/cprofile.html', context)


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders
    }
    return render(request, 'customers/my_orders.html', context)
