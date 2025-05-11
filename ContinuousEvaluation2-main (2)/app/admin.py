from django.contrib import admin
from . models import Cart, Customer, OrderPlaced, Payment, Product, Wishlist
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin

# Register your models here.

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','discounted_price','category','product_image','action_buttons']
    
    def action_buttons(self, obj):
        update_url = reverse('admin:app_product_change', args=[obj.id])
        delete_url = reverse('admin:app_product_delete', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background: #79aec8; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px; margin-right: 5px;">Update</a>'
            '<a class="button" href="{}" style="background: #ba2121; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px;">Delete</a>',
            update_url, delete_url
        )
    action_buttons.short_description = 'Actions'

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','name','email','locality','city','state','zipcode','action_buttons']
    list_editable = ['name']
    search_fields = ['name', 'user__email']
    
    def email(self, obj):
        return obj.user.email
        
    def action_buttons(self, obj):
        update_url = reverse('admin:app_customer_change', args=[obj.id])
        delete_url = reverse('admin:app_customer_delete', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background: #79aec8; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px; margin-right: 5px;">Update</a>'
            '<a class="button" href="{}" style="background: #ba2121; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px;">Delete</a>',
            update_url, delete_url
        )
    action_buttons.short_description = 'Actions'

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','products','quantity']
    def products(self,obj):
        link = reverse("admin:app_product_change",args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link, obj.product.title)

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','paid','action_buttons']
    
    def action_buttons(self, obj):
        update_url = reverse('admin:app_payment_change', args=[obj.id])
        delete_url = reverse('admin:app_payment_delete', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background: #79aec8; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px; margin-right: 5px;">Update</a>'
            '<a class="button" href="{}" style="background: #ba2121; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px;">Delete</a>',
            update_url, delete_url
        )
    action_buttons.short_description = 'Actions'

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin): 
    list_display=['id','user','customers','products','quantity','ordered_date','status','payments','action_buttons']
    def customers(self,obj):
        link=reverse('admin:app_customer_change',args=[obj.customer.pk])
        return format_html('<a href="{}">{}</a>',link,obj.customer.name)

    def products(self,obj):
        link=reverse('admin:app_product_change',args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link,obj.product.title)

    def payments(self,obj):
        link=reverse('admin:app_payment_change',args=[obj.payment.pk])
        return format_html('<a href="{}">{}</a>',link,obj.payment.razorpay_payment_id)
        
    def action_buttons(self, obj):
        update_url = reverse('admin:app_orderplaced_change', args=[obj.id])
        delete_url = reverse('admin:app_orderplaced_delete', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background: #79aec8; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px; margin-right: 5px;">Update</a>'
            '<a class="button" href="{}" style="background: #ba2121; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px;">Delete</a>',
            update_url, delete_url
        )
    action_buttons.short_description = 'Actions'

@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','products','action_buttons']
    def products(self,obj):
        link = reverse("admin:app_product_change",args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link, obj.product.title)
        
    def action_buttons(self, obj):
        update_url = reverse('admin:app_wishlist_change', args=[obj.id])
        delete_url = reverse('admin:app_wishlist_delete', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background: #79aec8; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px; margin-right: 5px;">Update</a>'
            '<a class="button" href="{}" style="background: #ba2121; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px;">Delete</a>',
            update_url, delete_url
        )
    action_buttons.short_description = 'Actions'

# Customize User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'action_buttons')
    list_editable = ('email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    def action_buttons(self, obj):
        update_url = reverse('admin:auth_user_change', args=[obj.id])
        delete_url = reverse('admin:auth_user_delete', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background: #79aec8; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px; margin-right: 5px;">Update</a>'
            '<a class="button" href="{}" style="background: #ba2121; padding: 5px 10px; color: white; text-decoration: none; border-radius: 4px;">Delete</a>',
            update_url, delete_url
        )
    action_buttons.short_description = 'Actions'

# Unregister the default UserAdmin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin) 