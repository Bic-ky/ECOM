from .models import Cart, Product


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            product = Product.objects.get(pk=item.product.id)
            subtotal += (product.value_of_share * item.quantity) # subtotal = subtotal + (product.value_of_share * item.quantity)
        
        grand_total = subtotal + (subtotal*(13/100))
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total)