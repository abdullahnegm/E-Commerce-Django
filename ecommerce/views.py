from django.shortcuts import render , get_object_or_404 , redirect
from django.views.generic import ListView , DetailView , View
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import stripe
import string
import random
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

from.forms import *
from .models import *
# Create your views here.

def create_ref_code():
    return "".join(random.choices( string.ascii_uppercase + string.digits , k=20 ))

class HomeView(ListView):
    model = Item
    template_name = "home-page.html"

class ItemData(DetailView):
    model = Item
    template_name = "product.html"

class OrderSummaryView( LoginRequiredMixin , View):
    def get(self , request , *args , **kwargs):
        try:
            orders = Order.objects.get( user = request.user , ordered = False )
            return render( request , "cart.html" , {"orders":orders})
        except ObjectDoesNotExist:
            messages.error(request , "You don't have an active order")
            return render( request , "cart.html")

class CheckOutView(View):
    def get(self , request , *args , **kwargs):
        orders = Order.objects.get( user = request.user , ordered = False )
        form = CheckoutForm()
        couponform = CouponForm()
        context = {"form" : form , "couponform"  :couponform , "orders" : orders }
        return render(request , "checkout.html" , context)

    def post(self , request , *args , **kwargs):
        form = CheckoutForm( request.POST or None )
        try:
            order = Order.objects.get( user = request.user , ordered = False )
            if form.is_valid():
                shipping_address = form.cleaned_data.get("shipping_address")
                shipping_address2 = form.cleaned_data.get("shipping_address2")
                shipping_country = form.cleaned_data.get("shipping_country")
                shipping_zip = form.cleaned_data.get("shipping_zip")
                billingaddress = BillingAddress(
                    user = request.user,
                    shipping_address = shipping_address,
                    shipping_address2 = shipping_address2,
                    shipping_country = shipping_country,
                    shipping_zip = shipping_zip
                )
                billingaddress.save()
                order.billing_address = billingaddress
                order.save()
                # payment_option = form.cleaned_data.get("payment_option")
                # if payment_option == "S" :
                #     return redirect("ecommerce:payment-method" , payment_option="stripe")
                # elif payment_option == "P" :
                #     return redirect("ecommerce:payment-method" , payment_option="paypal")
                return redirect("ecommerce:payment-method")
            messages.warning(request , "Invalid payment option selected")
            return render(request , "checkout.html" , {"form":form})
        except ObjectDoesNotExist:
            messages.warning(request , "You don't have an active order")
            return redirect("ecommerce:order-summary")
        
class PaymentMethod(View):
    def get(self , request , *args , **kwargs):
        orders = Order.objects.get( user=request.user , ordered = False)
        return render(request , "payment.html" , {"orders":orders})
    def post(self , request , *args , **kwargs):
        token = request.POST.get("stripeToken")
        order = Order.objects.get( user=request.user , ordered=False)
        amount = int(order.get_total_price() * 100)
        if amount == 0:
            amount = 50
        try:
    # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount=amount ,
                currency="usd" ,
                source=token ,
            )     
            
            payment = Payment()
            payment.stripe_charge_id = charge["id"]
            payment.user = request.user
            payment.amount = amount
            payment.save()
            
            order.ordered = True
            order.ref_code = create_ref_code()
            order.payment = payment
            order.save()
            
            order_item = order.items.all()
            order_item.update(ordered = True)
            for item in order_item:
                item.save()
        
            messages.error( request , "Your order was successful" )
            return redirect("ecommerce:home")
        #stripe error handling

        except stripe.error.CardError as e:
            messages.error( request , e.error.message )
            return redirect("1/")

        except stripe.error.RateLimitError as e:
            messages.error( request , "Rate limit Error" )
            return redirect("2/")

        except stripe.error.InvalidRequestError as e:
            messages.error( request , "Invalid Parameters" )
            return redirect("3/")

        except stripe.error.AuthenticationError as e:
            messages.error( request , "Not Authenticated" )
            return redirect("4/")

        except stripe.error.APIConnectionError as e:
            messages.error( request , "Connection Failed" )
            return redirect("5/")

        except stripe.error.StripeError as e:
            messages.error( request , "Something Went Wrong" )
            return redirect("6/")

        except Exception as e:
            messages.error( request , "A serious error occured, we have been notified" )
            return redirect("7/")
    


@login_required
def add_to_cart(request , slug):
    item = get_object_or_404( Item , slug = slug )
    order_item , created = OrderItem.objects.get_or_create( item = item ,
                user = request.user , ordered = False )
    order_qs = Order.objects.filter( user = request.user , ordered = False )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter( item__slug = item.slug ).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request , "This item quantity was updated.")
        else:
            messages.info(request , "This item was added to your cart")
            order.items.add( order_item )
    else:
        order_date = timezone.now()
        order = Order.objects.create( user = request.user , ordered_date=order_date )
        order.items.add( order_item )
        messages.info(request , "This item was added to your cart")
    return redirect( "ecommerce:order-summary")

@login_required
def remove_from_cart( request , slug ):
    item = get_object_or_404( Item , slug=slug )
    order_qs = Order.objects.filter( user = request.user , ordered = False )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter( item__slug = item.slug ):
            order_item = OrderItem.objects.filter( item = item ,
                user = request.user , ordered = False )[0]
            order.items.remove(order_item)
            messages.info(request , "This item has been removed from your cart")
            return redirect("ecommerce:order-summary")
        else:
            messages.info(request , "This item wasn't in your cart")
            return redirect("ecommerce:order-summary")
    else:
        messages.info(request , "This item wasn't in your cart")
        return redirect("ecommerce:order-summary")

@login_required
def remove_single_from_cart( request , slug ):
    item = get_object_or_404( Item , slug=slug )
    order_qs = Order.objects.filter( user = request.user , ordered = False )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter( item__slug = item.slug ):
            order_item = OrderItem.objects.filter( item = item ,
                user = request.user , ordered = False )[0]
            order_item.quantity -= 1
            if order_item.quantity == 0 :
                order.items.remove(order_item)
            else :
                order_item.save()        
            return redirect("ecommerce:order-summary")
        else:
            messages.info(request , "This item isn't in your cart")
            return redirect("ecommerce:order-summary")
    else:
        messages.info(request , "This item isn't in your cart")
        return redirect("ecommerce:order-summary")
    
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get( code = code )
        return coupon
    except ObjectDoesNotExist:
        messages.info(request , "This coupon doesn't exist")
        return redirect("ecommerce:check-out")

class add_coupon(View):
    def post(self , request , *args , **kwargs):
        form = CouponForm( request.POST or None)
        if form.is_valid():
            try:
                order = Order.objects.get( user=request.user , ordered = False )
                code = form.cleaned_data.get("code")
                order.coupon = get_coupon( request , code )
                order.save()
                messages.success(request ,"Successfuly added coupon")
                return redirect("ecommerce:check-out")
            except ObjectDoesNotExist:
                messages.info(request ,"You don't have an active order")
                return redirect("ecommerce:check-out")
        else :
            return None

class RefundView(View):
    def get( self , request , *args , **kwargs ):
        form = RefundForm()
        return render( request , "refund_request.html" , {"form":form} )
    def post( self , request , *args , **kwargs ):
        form = RefundForm(request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get("ref_code")
            message = form.cleaned_data.get("message")
            email = form.cleaned_data.get("email")
            try:
                order = Order.objects.get( ref_code = ref_code )
                order.refund_request = True
                order.save()
                
                refund = Refund()
                refund.order = order
                refund.message = message
                refund.email = email
                refund.save()

                messages.info( request , "Your request was received")
                return redirect("ecommerce:home")
            except ObjectDoesNotExist:
                messages.info( request , "This order referrence doesn't exist" )
                return redirect("ecommerce:refund")