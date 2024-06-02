from django.shortcuts import render
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django.core.paginator import Paginator
from account.models import User, UserProfile
from shop.models import Category , Product


# Create your views here.
def shop_view(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    # top_products = Product.objects.filter(is_available=True).order_by(
    #     '-percent_return_after_due_date')[:3]
    page = request.GET.get('page')
    search_query = request.GET.get('search_query')
    sort_by = request.GET.get('sort_by')

    # if sort_by == 'percent_return':
    #     product = products.order_by('-percent_return_after_due_date')
    # elif sort_by == 'duration':
    #     product = products.order_by(F('return_date') - F('created_at'))
    # elif sort_by == 'value_of_share':
    #     product = products.order_by('value_of_share')

    if search_query and search_query.strip() != '':
        product_ids = []
        for product in products:
            if (product.product_title and product.product_title.lower().find(search_query.lower()) != -1) or \
                    (product.address and product.address.lower().find(search_query.lower()) != -1):
                product_ids.append(product.id)

        user_profile_ids = [profile.user.id for profile in UserProfile.objects.filter(
            Q(first_name__icontains=search_query) | Q(
                last_name__icontains=search_query)
        )]

        vendor_ids = [vendor.id for vendor in User.objects.filter(
            Q(id__in=user_profile_ids) & Q(role=User.VENDOR)
        )]

        products = products.filter(Q(id__in=product_ids) | Q(vendor_id__in=vendor_ids))


    paginator = Paginator(products, 8)
    product_page = paginator.get_page(page)
    print(product_page)
    context = {
        # 'top_Products': top_products,
        'categories': categories,
        'Product_page': product_page,
        'sort_by': sort_by,
        'Products': products
    }

    return render(request, 'shop/product.html', context)



def product_detail(request):
    return render(request, "shop/prod_detail.html")

def cart(request):
    return render(request , "shop/cart.html")

def checkout(request):
    return render(request , "shop/checkout.html")