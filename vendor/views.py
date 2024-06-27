
from django.shortcuts import get_object_or_404, redirect, render
from customers.forms import UserProfileForm
from orders.models import Order, ProductOrder
from shop.models import Category, Product
from vendor.forms import VendorForm
from shop.forms import ProductItemForm

from account.models import UserProfile
from .models import  Vendor
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from account.views import check_role_vendor

from django.template.defaultfilters import slugify

@login_required(login_url='login')
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        print(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        print(profile_form)
        if profile_form.is_valid() :
            profile_form.save()
            messages.success(request, 'Profile updated')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            
    else:
       
        profile_form = UserProfileForm(instance=profile)
        

    context = {
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'vendor/vprofile.html', context)



def get_vendor(request):
    try:
        return Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        return None


from django.db.models import Count , Prefetch
from shop.models import Category

def product_builder(request):
    # Prefetch related products for each category
    categories = Category.objects.annotate(num_projects=Count('products')).prefetch_related(
        Prefetch('products', queryset=Product.objects.all())
    ).order_by('created_at')
    
    for category in categories:
        print(category.products.all())  # Debug: print related products for each category
    
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/product_builder.html', context)



def add_product(request):
    vendor = get_vendor(request)
    print(f"Vendor: {vendor}")  # Debugging line
    
    if vendor is None:
        messages.error(request, 'You are not authorized to add products.')
      

    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES)
        if form.is_valid():
            productTitle = form.cleaned_data['product_title']
            product = form.save(commit=False)
            product.vendor = vendor  # Ensure vendor is set
            product.slug = slugify(productTitle)
            product.save()
            messages.success(request, 'Product Item added successfully!')
            return redirect("product_category")
        else:
            print(form.errors)
    else:
        form = ProductItemForm()
        # Optionally, filter categories based on vendor if needed
        # form.fields['category'].queryset = Category.objects.filter(vendor=vendor)

    context = {
        'form': form,
    }
    return render(request, 'vendor/add_product.html', context)



def productItem_by_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    productItems = Product.objects.filter(category=category)
    print(productItems.query)  # Print the SQL query
    
    context = {
        'productItems': productItems,
        'category': category,
    }
    return render(request, 'vendor/productItem_by_category.html', context)


# @login_required(login_url='login')
# @user_passes_test(check_role_vendor)
def edit_product(request, pk=None):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            productTitle = form.cleaned_data['product_title']
            product = form.save(commit=False)
            product.slug = slugify(productTitle)
            form.save()
            messages.success(request, 'Product Item updated successfully!')
            return redirect('product_category', product.category.id)
        else:
            print(form.errors)

    else:
        form = ProductItemForm(instance=product)
        # form.fields['category'].queryset = Category.objects.f
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'vendor/edit_product.html', context)


# @login_required(login_url='login')
# @user_passes_test(check_role_vendor)
def delete_product(request, pk=None):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'product Item has been deleted successfully!')
    return redirect('product_category', product.category.id)



def my_orders(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'vendor/my_orders.html', context)



def order_detail(request, order_number):
    try:
        order = get_object_or_404(Order, order_number=order_number)
        ordered_product = ProductOrder.objects.filter(order=order)
        print(ordered_product)
        context = {
            'order': order,
            'ordered_product': ordered_product,
            'subtotal':order.total - order.total_tax, # Assuming this method exists in your Order model
            'tax_data': order.get_total_by_vendor(vendor=request.user)['tax_dict'],
            'grand_total': order.get_total_by_vendor(vendor=request.user)['grand_total'],
        }
        
        print(context)
        return render(request, 'vendor/order_detail.html', context)
    except Order.DoesNotExist:
        return redirect('vendor')  # Redirect to vendor page if order does not exist

# def my_orders(request):
#     vendor = Vendor.objects.get(user=request.user)
#     orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('created_at')

#     context = {
#         'orders': orders,
#     }
#     return render(request, 'vendor/my_orders.html', context)