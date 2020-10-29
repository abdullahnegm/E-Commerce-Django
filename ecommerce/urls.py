from django.urls import path


from .views import *
app_name = "ecommerce"

urlpatterns = [
    path("home/" , HomeView.as_view() , name="home" ),
    path("product/<slug>" , ItemData.as_view() , name="product" ),
    path("add-to-cart/<slug>" , add_to_cart , name="add-to-cart" ),
    path("remove-from-cart/<slug>" , remove_from_cart , name="remove-from-cart" ),
    path("remove-single-cart/<slug>" , remove_single_from_cart , name="remove-single-cart" ),
    path("order-summary/" , OrderSummaryView.as_view() , name="order-summary" ),
    path("check-out/" , CheckOutView.as_view() , name="check-out" ),
    path("payment/" , PaymentMethod.as_view() , name="payment-method" ),
    path("check-out/add-coupon" , add_coupon.as_view() , name="add-coupon" ),
    path("refund/" , RefundView.as_view() , name="refund" ),
]