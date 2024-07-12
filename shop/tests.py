from django.test import TestCase
from shop.models import Product, Cart, Category
from account.models import User

class ModelsTestCase(TestCase):
    def setUp(self):
        # Create a user and associated user profile
        self.user = User.objects.create_user(
            first_name='Customer',
            last_name='Test',
            username='Customer',
            email='Customer@test.com',
            password='testpassword'
        )
        # Create a category
        self.category = Category.objects.create(category_name='Test Category', description='Test Description')

        # Create a product
        self.product = Product.objects.create(
            product_title='Cloth',
            category=self.category,
            description='A fashionable clth.',
            price=999.99,
            image='product_images/cloth.png',
            is_available=True
        )

    def test_cart_creation(self):
        cart = Cart.objects.create(
            user=self.user,
            project=self.product,
            quantity=1
        )

        # Print the cart details
        print(f"Cart Item: User={cart.user.username}, Product={cart.project.product_title}, Quantity={cart.quantity}")

        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.project, self.product)
        self.assertEqual(cart.quantity, 1)
        self.assertIsNotNone(cart.created_at)
        self.assertIsNotNone(cart.updated_at)

    def test_product_creation(self):
        # Print the product details
        print(f"Product: Title={self.product.product_title}, Price={self.product.price}, Category={self.product.category.category_name}")

        self.assertEqual(self.product.product_title, 'Cloth')
        self.assertEqual(self.product.price, 999.99)
        self.assertEqual(self.product.category, self.category)
        self.assertTrue(self.product.is_available)
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)