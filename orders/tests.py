from django.test import TestCase, Client
from django.urls import reverse
from account.models import User, UserProfile
from .models import Order, Payment, ProductOrder
from shop.models import Cart, Category, Product
from django.core.exceptions import PermissionDenied
import json

class PaymentsViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='password',
            email='testuser@gmail.com',
            role=User.CUSTOMER  # Set the role directly
        )
        self.client = Client()

        # Create a category
        self.category = Category.objects.create(
            category_name='Electronics',
        )

        # Create a product
        self.product = Product.objects.create(
            product_title='Laptop',
            category=self.category,
            description='A high-performance laptop.',
            price=999.99,
            image='product_images/laptop.png',
            is_available=True
        )

        self.order = Order.objects.create(
            user=self.user,
            order_number='TEST123',
            total=999.99,
            tax_data='{}',
            total_tax=0.00,
            payment_method='PayPal',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            email='testuser@example.com',
            address='Test Address',
            city='Test City'
        )

        # Create a ProductOrder related to the order
        self.product_order = ProductOrder.objects.create(
            order=self.order,
            user=self.user,
            product=self.product,
            quantity=1,
            price=self.product.price,
            amount=self.product.price * 1,
        )
        
        # Create a test cart item
        self.cart_item = Cart.objects.create(
            user=self.user,
            project=self.product,
            quantity=1
        )

    def test_payments_view(self):
        self.client.force_login(self.user)
        
        print(f"User: {self.user.username}")
        print(f"User role: {self.user.get_role()}")
        print(f"Is authenticated: {self.user.is_authenticated}")
        print(f"User role value: {self.user.role}")
        
        from account.views import check_role_customer
        try:
            result = check_role_customer(self.user)
            print(f"Passes check_role_customer: {result}")
        except PermissionDenied:
            print("check_role_customer raised PermissionDenied")
        
        print(f"Payments URL: {reverse('payments')}")
        
        # First, try a GET request
        get_response = self.client.get(reverse('payments'))
        print(f"GET Response status code: {get_response.status_code}")
        
        post_data = {
            'order_number': self.order.order_number,
            'transaction_id': 'TEST_TRANSACTION_123',
            'payment_method': 'PayPal',
            'status': 'COMPLETED'
        }
        
        response = self.client.post(
            reverse('payments'),
            data=json.dumps(post_data),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"POST Response status code: {response.status_code}")
        print(f"POST Response content: {response.content}")
        
        if response.status_code == 302:
            print(f"POST Redirect location: {response.url}")
        
        self.assertEqual(response.status_code, 200)