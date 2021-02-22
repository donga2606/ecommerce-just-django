from django.db import models
from django.conf import settings
from django.db.models.enums import Choices
from django.urls import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Out wear'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null = True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()

    def __str__(self):
        return self.title    

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'slug': self.slug})
    
    def get_add_to_cart_url(self):
        return reverse('core:add_to_cart', kwargs={
            'slug': self.slug,
        })

    def get_remove_from_cart_url(self):
        return reverse('core:remove_from_cart', kwargs={'slug': self.slug})





class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_totals(self):
        return self.item.price * self.quantity

    def get_totals_discount(self):
        return self.item.discount_price * self.quantity

    def get_amount_saved(self):
        return self.get_totals() - self.get_totals_discount()

    def get_final_totals(self):
        if self.item.discount_price:
            return self.get_totals_discount()
        return self.get_totals()



# Shopping cart, when login, when add to card, when check out:
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_totals()
        return total
    
class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username







        
    