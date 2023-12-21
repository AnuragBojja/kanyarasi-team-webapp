from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Master(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username  

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_short_name(self):
        return self.user.first_name

    # Additional methods and logic for Master

class MenuItem(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    image_url = models.URLField()
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('user', 'User'),
        ('master', 'Master'),
        ('captain', 'Captain'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField(MenuItem)
    order_date = models.DateTimeField(default=timezone.now)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    pincode = models.CharField(max_length=10)
    address_line_1 = models.CharField(max_length=255,default='Default Address')
    address_line_2 = models.CharField(max_length=255, blank=True)
    tracking_number = models.CharField(max_length=10, blank=True, null=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'


class CompletedOrder(models.Model):
    original_order = models.OneToOneField(Order, on_delete=models.CASCADE)
    user_address = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Completed Order {self.original_order.id} for {self.original_order.user.username}"

    @property
    def item_list(self):
        return self.original_order.items.all()
