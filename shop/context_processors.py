from .models import Cart, Product, Tax


# def get_cart_counter(request):
#     cart_count = 0
#     if request.user.is_authenticated:
#         try:
#             cart_items = Cart.objects.filter(user=request.user)
#             if cart_items:
#                 for cart_item in cart_items:
#                     cart_count += cart_item.quantity
#             else:
#                 cart_count = 0
#         except:
#             cart_count = 0
#     return dict(cart_count=cart_count)


# def get_cart_amounts(request):
#     subtotal = 0
#     tax = 0
#     grand_total = 0
#     tax_dict = {}
#     if request.user.is_authenticated:
#         cart_items = Cart.objects.filter(user=request.user)
#         for item in cart_items:
#             product = Product.objects.get(pk=item.product.id)
#             subtotal += (product.value_of_share * item.quantity) # subtotal = subtotal + (product.value_of_share * item.quantity)
        
#         grand_total = subtotal + (subtotal*(13/100))
#     return dict(subtotal=subtotal, tax=tax, grand_total=grand_total)


def get_cart_counter(request):
    cart_count = Cart.objects.filter(user=request.user).count()
    return {'cart_count': cart_count}

def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = {}
    # subtotal = sum(item.quantity for item in cart_items)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            project = Product.objects.get(pk=item.project.id)
            subtotal += (project.price * item.quantity) # subtotal = subtotal + (project.value_of_share * item.quantity)

        get_tax = Tax.objects.filter(is_active=True)
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage) : tax_amount}})
        
        tax = sum(x for key in tax_dict.values() for x in key.values())
        grand_total = subtotal + tax
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)  # Modify this to include tax if needed
