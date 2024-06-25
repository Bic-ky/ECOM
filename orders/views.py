
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render, redirect
from orders.utils import generate_order_number
from shop.models import Cart, Tax
from shop.context_processors import get_cart_amounts
from shop.models import Product
from .forms import OrderForm
from .models import Order
import json
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F

def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("shop")

    vendors_user_ids = []
    for i in cart_items:
        if i.project.vendor.user.id not in vendors_user_ids:
            vendors_user_ids.append(i.project.vendor.user.id)

    subtotal = get_cart_amounts(request)["subtotal"]
    total_tax = get_cart_amounts(request)["tax"]
    grand_total = get_cart_amounts(request)["grand_total"]
    tax_data = get_cart_amounts(request)["tax_dict"]

    if request.method == "POST":

        form = OrderForm(request.POST)
        if form.is_valid():
            print("POST Data:")
            for key, value in request.POST.items():
                print(f"{key}: {value}")
            order = Order()
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]

            # Remove country code and keep the last 10 digits of the phone number
            phone_number = form.cleaned_data["phone"]
            form.cleaned_data["phone"] = phone_number
            order.phone = phone_number
            for cart_item in cart_items:
                order.project = cart_item.project
            order.email = form.cleaned_data["email"]
            order.address = form.cleaned_data["address"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data, cls=DjangoJSONEncoder)
            order.total_tax = total_tax
            order.payment_method = request.POST["payment_method"]
            order.save()
            order_number = generate_order_number(order.id)
            order.order_number = order_number
            order.save()

            # Store the modified order form data and order number in the session
            request.session["order_form_data"] = form.cleaned_data
            request.session["order_number"] = order_number

            # Print session data in the terminal
            print("Session Data:", request.session["order_form_data"])
            print("Order Number:", request.session["order_number"])

            form = OrderForm()
            context = {"order": order, "form": form, "cart_items": cart_items}
            return render(request, "orders/place_order.html", context)
        else:
            print(form.errors)

    return render(request, "orders/place_order.html")

