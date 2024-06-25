from django.shortcuts import render
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django.core.paginator import Paginator
from account.models import User, UserProfile
from orders.forms import OrderForm
from .context_processors import get_cart_amounts, get_cart_counter
from shop.models import Cart, Category , Product, Tax
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



@login_required
def cart(request):
    try:
        cart_items = Cart.objects.filter(user=request.user)
        context = {'cart_items': cart_items}
        return render(request, 'shop/cart.html', context)
    except Exception as e:
        logger.error(f'Error in cart view: {str(e)}')
        return render(request, 'shop/cart.html', {'error': 'An unexpected error occurred'})

@login_required
def add_to_cart(request, product_id):
    logger.info(f'add_to_cart called with product_id: {product_id}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            product = get_object_or_404(Product, id=product_id)
            logger.info(f'Product found: {product}')
            cart_item, created = Cart.objects.get_or_create(user=request.user, project=product)
            logger.info(f'Cart item: {cart_item}, created: {created}')
            if not created:
                cart_item.quantity = (cart_item.quantity or 0) + 1  # Ensure quantity is not None
                cart_item.save()
                logger.info(f'Increased quantity for cart item: {cart_item}')
            else:
                logger.info(f'Created new cart item: {cart_item}')
            return JsonResponse({
                'status': 'Success',
                'message': 'Increased the cart quantity' if not created else 'Product added to the cart',
                'cart_counter': get_cart_counter(request),
                'qty': cart_item.quantity,
                'cart_amount': get_cart_amounts(request)
            })
        except Product.DoesNotExist:
            logger.error(f'Product with id {product_id} does not exist.')
            return JsonResponse({'status': 'Failed', 'message': 'This product does not exist!'})
        except Exception as e:
            logger.error(f'Unexpected error in add_to_cart: {str(e)}')
            return JsonResponse({'status': 'Failed', 'message': 'An unexpected error occurred'})
    else:
        return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})

@login_required
def decrease_cart(request, product_id):
    logger.info(f'decrease_cart called with product_id: {product_id}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            product = get_object_or_404(Product, id=product_id)
            cart_item = get_object_or_404(Cart, user=request.user, project=product)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                cart_item.quantity = 0
            logger.info(f'Cart updated successfully for product_id: {product_id}')
            return JsonResponse({
                'status': 'Success',
                'cart_counter': get_cart_counter(request),
                'qty': cart_item.quantity,
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

@login_required
def delete_cart(request, cart_id):
    logger.info(f'delete_cart called with cart_id: {cart_id}')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            cart_item = get_object_or_404(Cart, user=request.user, id=cart_id)
            cart_item.delete()
            logger.info(f'Cart item deleted successfully with cart_id: {cart_id}')
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




def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('shop')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request,'shop/checkout.html',context )