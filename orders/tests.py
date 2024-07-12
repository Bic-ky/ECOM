from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth import get_user_model
from django.utils import timezone

from orders.models import Order  # Import your Order model
from orders.forms import OrderForm  # Import your OrderForm
from orders.views import place_order  # Import your view function
from shop.models import Cart, Category, Product  # Import your Cart model

class PlaceOrderViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser', email='test@example.com', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')

        # Create a category
        self.category = Category.objects.create(category_name='Test Category', description='Test Category Description')

        # Create a product
        self.product = Product.objects.create(
            category=self.category,
            vendor=None,
            product_title='Test Product',
            slug='test-product',
            description='Test product description',
            price=100.00,
            image='product_images/test_product.jpg',
            is_available=True
        )

        # Create a sample cart item for the user
        self.cart_item = Cart.objects.create(
            user=self.user,
            project=self.product, # Replace with a valid product instance
            quantity=1,
            price=10.0,
            amount=10.0,
            created_at=timezone.now()
        )

    def test_place_order_view(self):
        # Setup session and request
        session = self.client.session
        session['cart_id'] = self.cart_item.id  # Store cart item ID in session
        session.save()

        # Simulate POST data
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890',
            'email': 'john.doe@example.com',
            'address': '123 Test St',
            'country': 'US',
            'state': 'CA',
            'city': 'San Francisco',
            'payment_method': 'PayPal',
        }

        # Make POST request to place_order view
        response = self.client.post(reverse('place_order'), data)

        # Check if the order was created successfully
        self.assertEqual(response.status_code, 200)  # Assuming you return 200 on success
        self.assertContains(response, 'Order Number')  # Assuming 'Order Number' is in the response

        # Check if the order object exists in the database
        self.assertTrue(Order.objects.filter(user=self.user).exists())

        # Optionally, check session data
        self.assertIn('order_form_data', self.client.session)
        self.assertIn('order_number', self.client.session)
        saved_form_data = self.client.session['order_form_data']
        saved_order_number = self.client.session['order_number']
        self.assertEqual(saved_form_data['email'], 'john.doe@example.com')
        self.assertEqual(saved_order_number, Order.objects.latest('created_at').order_number)

        # Clean up: Clear session data after test
        del self.client.session['cart_id']
        self.client.session.save()
