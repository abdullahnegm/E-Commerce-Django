from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django_countries.fields import CountryField
# Create your models here.

CATEGORY_CHOICES = (
    ( "S" , "Shirt" ),
    ( "SW" , "Sport Wear" ),
    ( "OW" , "Out Wear" )
)

LABEL_CHOICES = (
    ( "P" , "primary" ),
    ( "S" , "secondry" ),
    ( "D" , "danger" )
)


class Item(models.Model):
    title = models.CharField( max_length = 100 )
    price = models.FloatField()
    dis_price = models.FloatField( blank=True , null=True )
    category = models.CharField( choices=CATEGORY_CHOICES , max_length=2 )
    label = models.CharField( choices=LABEL_CHOICES , max_length=1 )
    slug = models.SlugField()
    description = models.TextField()
    img = models.ImageField()
    

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse( "ecommerce:product" , kwargs={"slug":self.slug} )

    def get_add_to_cart_url(self):
        return reverse( "ecommerce:add-to-cart" , kwargs={"slug":self.slug} )

    def get_remove_from_cart_url(self):
        return reverse( "ecommerce:remove-from-cart" , kwargs={"slug":self.slug} )
    
        
class OrderItem(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE )
    ordered = models.BooleanField( default=False )
    item = models.ForeignKey( Item , on_delete=models.CASCADE )
    quantity = models.IntegerField( default = 1 )

    def __str__(self):
        return f"{ self.quantity } of { self.item.title }"

    # def get_total_dis_price(self):
    #     return self.quantity * self.item.dis_price
    
    def get_final_price(self):
        if self.item.dis_price :
            return self.item.dis_price
        else:
            return self.item.price
    
    def get_total_price(self):
        return self.get_final_price() * self.quantity
        

class Order(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE )
    ref_code = models.CharField( max_length=20 )
    items = models.ManyToManyField( OrderItem )
    start_date = models.DateTimeField( auto_now_add=True )
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField( default=False )
    billing_address = models.ForeignKey("BillingAddress" , on_delete=models.SET_NULL , blank=True , null=True)
    payment = models.ForeignKey("Payment" , on_delete=models.SET_NULL , blank=True , null=True)
    coupon = models.ForeignKey("Coupon" , on_delete=models.SET_NULL , blank=True , null=True)
    being_delivered = models.BooleanField( default=False )
    received = models.BooleanField( default=False )
    refund_request = models.BooleanField( default=False )
    refund_accept = models.BooleanField( default=False )

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total = sum( i.get_final_price() * i.quantity for i in self.items.all() )
        if self.coupon:
            total -= self.coupon.amount
        total = 0 if total < 0 else total
        return total

class BillingAddress(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    shipping_address = models.CharField( max_length = 100 )
    shipping_address2 = models.CharField( max_length = 100 )
    shipping_country = CountryField( multiple=  True )
    shipping_zip = models.CharField( max_length = 100 )

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User , on_delete=models.SET_NULL , blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    
    def __str__(self):
        return self.code
    
class Refund(models.Model):
    order = models.ForeignKey( Order , on_delete=models.CASCADE )
    message = models.TextField()
    accepted = models.BooleanField( default=False )
    email = models.EmailField( )

    def __str__(self):
        return f"{self.id}"