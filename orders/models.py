
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Rs {self.price})"


class Table(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('PARTIALLY_OCCUPIED', 'Partially Occupied'),
        ('FULL', 'Full'),
    ]

    table_number = models.IntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=4)
    current_occupancy = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')

    @property
    def available_seats(self):
        return max(0, self.capacity - self.current_occupancy)

    def update_occupancy_status(self):
        
        if self.current_occupancy == 0:
            self.status = 'AVAILABLE'
        elif self.current_occupancy >= self.capacity:
            self.status = 'FULL'
        else:
            self.status = 'PARTIALLY_OCCUPIED'
        self.save()

    def __str__(self):
        return f"Table {self.table_number} ({self.current_occupancy}/{self.capacity} Seated)"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready To Serve'),
        ('SERVED', 'Served'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    party_size = models.PositiveIntegerField(default=1)
    server = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    customer_name = models.CharField(max_length=100, blank=True, default="Guest")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - Table {self.table.table_number if self.table else 'Takeout'} [{self.status}]"

    def calculate_totals(self, tax_rate=Decimal('0.00')):
       
        items_subtotal = sum(item.subtotal for item in self.items.all())
        self.subtotal = items_subtotal
        self.tax_amount = items_subtotal * tax_rate
        self.grand_total = self.subtotal    + self.tax_amount
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unit_price and self.menu_item:
            self.unit_price = self.menu_item.price
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name if self.menu_item else 'Item'} (Order #{self.order.id})"
