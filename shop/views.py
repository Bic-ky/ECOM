from django.shortcuts import render
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django.core.paginator import Paginator
from account.models import User, UserProfile
from .context_processors import get_cart_amounts, get_cart_counter
from shop.models import Cart, Category , Product
from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404,redirect
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required , user_passes_test
from account.views import check_role_customer

import logging  

logger = logging.getLogger(__name__)
# Create your views here.
def shop_view(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    page = request.GET.get('page')
    search_query = request.GET.get('search_query')
    sort_by = request.GET.get('sort_by')

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


        products = products.filter(Q(id__in=product_ids))


    paginator = Paginator(products, 8)
    product_page = paginator.get_page(page)
    print(product_page)
    context = {
        # 'top_Products': top_products,
        'categories': categories,
        'product_page': product_page,
        'sort_by': sort_by,
        'products': products
    }

    return render(request, 'shop/product.html', context)



def product_detail(request , id):
    product = get_object_or_404(Product, id=id)
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    
    context = {
        'product': [product],
        # 'related_products': related_products,
        'cart_items': cart_items,
    }
    return render(request, "shop/prod_detail.html" , context)


def cart(request):
    try:
        cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
        context = {'cart_items': cart_items}
        return render(request, 'shop/cart.html', context)
    except Exception as e:
        logger.error(f'Error in cart view: {str(e)}')
        return render(request, 'shop/cart.html', {'error': 'An unexpected error occurred'})

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

    try:
        product = get_object_or_404(Product, id=product_id)
        chkCart = Cart.objects.get_or_create(user=request.user, project=product)
        if chkCart.quantity < 5:
            chkCart.quantity += 1
            chkCart.save()
            return JsonResponse({
                'status': 'Success', 
                'message': 'Increased the cart quantity', 
                'cart_counter': get_cart_counter(request), 
                'qty': chkCart.quantity, 
                'cart_amount': get_cart_amounts(request)
            })
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Maximum share limit reached '})
    except Product.DoesNotExist:
        logger.error(f'Product with id {product_id} does not exist.')
        return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})
    except ValidationError as e:
        error_message = ' '.join(e.messages)
        logger.error(f'Validation error: {error_message}')
        return JsonResponse({'status': 'Failed', 'message': error_message})
    except Exception as e:
        logger.error(f'Unexpected error in add_to_cart: {str(e)}')
        return JsonResponse({'status': 'Failed', 'message': 'An unexpected error occurred'})

def decrease_cart(request, product_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                product = get_object_or_404(Product, id=product_id)
                chkCart = get_object_or_404(Cart, user=request.user, project=product)
                if chkCart.quantity > 1:
                    chkCart.quantity -= 1
                    chkCart.save()
                else:
                    chkCart.delete()
                    chkCart.quantity = 0
                return JsonResponse({
                    'status': 'Success', 
                    'cart_counter': get_cart_counter(request), 
                    'qty': chkCart.quantity,
                    'cart_amount': get_cart_amounts(request)
                })
            except Cart.DoesNotExist:
                logger.error(f'Cart item for product {product_id} does not exist.')
                return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except Product.DoesNotExist:
                logger.error(f'Product with id {product_id} does not exist.')
                return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})
            except Exception as e:
                logger.error(f'Unexpected error in decrease_cart: {str(e)}')
                return JsonResponse({'status': 'Failed', 'message': 'An unexpected error occurred'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = get_object_or_404(Cart, user=request.user, id=cart_id)
                cart_item.delete()
                return JsonResponse({
                    'status': 'Success', 
                    'message': 'Cart item has been deleted!', 
                    'cart_counter': get_cart_counter(request),
                    'cart_amount': get_cart_amounts(request)
                })
            except Cart.DoesNotExist:
                logger.error(f'Cart item with id {cart_id} does not exist.')
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist!'})
            except Exception as e:
                logger.error(f'Unexpected error in delete_cart: {str(e)}')
                return JsonResponse({'status': 'Failed', 'message': 'An unexpected error occurred'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})






def checkout(request):
    return render(request , "shop/checkout.html")