
from django.shortcuts import get_object_or_404, redirect, render
from customers.forms import UserProfileForm
from shop.models import Category
from vendor.forms import VendorForm
from shop.forms import ProductItemForm

from account.models import UserProfile
from .models import  Vendor
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from account.views import check_role_vendor
from django.template.defaultfilters import slugify


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor



def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance = profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/vprofile.html', context)





# @login_required(login_url='login')
# @user_passes_test(check_role_vendor)
# def productitems_by_category(request, pk=None):
#     vendor = get_vendor(request)
#     category = get_object_or_404(Category, pk=pk)
#     productitems = productItem.objects.filter(vendor=vendor, category=category)
#     context = {
#         'productitems': productitems,
#         'category': category,
#     }
#     return render(request, 'vendor/productitems_by_category.html', context)




# @login_required(login_url='login')
# @user_passes_test(check_role_vendor)
def add_product(request):
    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES)
        if form.is_valid():
            productTitle = form.cleaned_data['product_title']
            product = form.save(commit=False)
            product.vendor = get_vendor(request)
            product.slug = slugify(productTitle)
            form.save()
            messages.success(request, 'product Item added successfully!')
            return redirect('productitems_by_category', product.category.id)
        else:
            print(form.errors)
    else:
        form = ProductItemForm()
        # modify this form
        # form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_product.html', context)



# @login_required(login_url='login')
# @user_passes_test(check_role_vendor)
# def edit_product(request, pk=None):
#     product = get_object_or_404(productItem, pk=pk)
#     if request.method == 'POST':
#         form = productItemForm(request.POST, request.FILES, instance=product)
#         if form.is_valid():
#             producttitle = form.cleaned_data['product_title']
#             product = form.save(commit=False)
#             product.vendor = get_vendor(request)
#             product.slug = slugify(producttitle)
#             form.save()
#             messages.success(request, 'product Item updated successfully!')
#             return redirect('productitems_by_category', product.category.id)
#         else:
#             print(form.errors)

#     else:
#         form = productItemForm(instance=product)
#         form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
#     context = {
#         'form': form,
#         'product': product,
#     }
#     return render(request, 'vendor/edit_product.html', context)


# @login_required(login_url='login')
# @user_passes_test(check_role_vendor)
# def delete_product(request, pk=None):
#     product = get_object_or_404(productItem, pk=pk)
#     product.delete()
#     messages.success(request, 'product Item has been deleted successfully!')
#     return redirect('productitems_by_category', product.category.id)


# def opening_hours(request):
#     opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
#     form = OpeningHourForm()
#     context = {
#         'form': form,
#         'opening_hours': opening_hours,
#     }
#     return render(request, 'vendor/opening_hours.html', context)


# def order_detail(request, order_number):
#     try:
#         order = Order.objects.get(order_number=order_number, is_ordered=True)
#         ordered_product = Orderedproduct.objects.filter(order=order, productitem__vendor=get_vendor(request))

#         context = {
#             'order': order,
#             'ordered_product': ordered_product,
#             'subtotal': order.get_total_by_vendor()['subtotal'],
#             'tax_data': order.get_total_by_vendor()['tax_dict'],
#             'grand_total': order.get_total_by_vendor()['grand_total'],
#         }
#     except:
#         return redirect('vendor')
#     return render(request, 'vendor/order_detail.html', context)


# def my_orders(request):
#     vendor = Vendor.objects.get(user=request.user)
#     orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('created_at')

#     context = {
#         'orders': orders,
#     }
#     return render(request, 'vendor/my_orders.html', context)