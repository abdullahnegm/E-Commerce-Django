from django.contrib import admin


from .models import *
# Register your models here.

def grant_refund( modeladmin , request , queryset ):
    queryset.update( refund_request = False , refund_accept = True )
grant_refund.short_description = "Update orders to refund granted"

class OrderAdmin(admin.ModelAdmin):
    list_display = ["user" , "ordered" , "being_delivered" , "received" , "refund_request" , "refund_accept"]
    list_filter = ["ordered" , "being_delivered" , "received" , "refund_request" , "refund_accept"]
    search_fields = ["user_username" , "ref_code"]
    actions = [grant_refund]
admin.site.register( Item )
admin.site.register( OrderItem )
admin.site.register( Order , OrderAdmin )
admin.site.register( Payment )
admin.site.register( Coupon )