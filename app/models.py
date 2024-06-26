from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import random
import string

CATEGORY_CHOICES = [
    ('OV', 'Oversized T-Shirts'),
    ('TS', 'T-Shirts'),
    ('JA', 'Jackets'),
    ('HO', 'Hoodies'),
    ('SW', 'Sweatshirt'),
    ('CA', 'Cargo Pants'),
    ('BA', 'Backprint t-shirts'),
    ('AN', 'Anime-themed Apparel'),
]

# Define choices for states
STATES = [
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
]

# Define choices for item sizes
SIZE_CHOICES = [
    ('XS', 'Extra Small'),
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('XL', 'Extra Large'),
]

ORDER_STATES = [
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Processed', 'Processed'),
    ('Shipped', 'Shipped'),
    ('Out for delivery', 'Out for Delivery'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
    ('Returned', 'Returned'),
]

class Product(models.Model):
    title = models.CharField(max_length=255)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.ImageField(upload_to='product')
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)

    def __str__(self):
        return self.title

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    locality = models.CharField(max_length=300)
    city = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)
    zipcode = models.CharField(max_length=6)
    state = models.CharField(choices=STATES, max_length=100)

    def __str__(self):
        return self.name


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"

    def get_item_price(self):
        return self.quantity * self.product.discount_price

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be a positive integer.")

    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, blank=False, null=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} ({self.size})"

    def total_price(self):
        return self.quantity * self.product.discount_price

    def increase_quantity(self):
        self.quantity += 1
        self.save()

    def get_item_price(self):
        return self.quantity * self.product.discount_price

    def decrease_quantity(self):
        if self.quantity > 1:
            self.quantity -= 1
            self.save()


def generate_order_id():
    while True:
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Order.objects.filter(order_id=order_id).exists():
            return order_id


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=False, null=True)
    razorpay_payment_status = models.CharField(max_length=100, blank=False, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=False, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment #{self.id} by {self.user.username}"


#order
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=6, unique=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, blank=False, null=False)
    quantity = models.PositiveIntegerField()
    order_state = models.CharField(max_length=16, choices=ORDER_STATES, default='pending')
    number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    state = models.CharField(choices=STATES, max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    mode_of_payment = models.CharField(max_length=50, choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')], default='COD')
    added_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = generate_order_id()
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_id} by {self.user.username}, Size: {self.size}, Quantity: {self.quantity}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, blank=False, null=False)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  