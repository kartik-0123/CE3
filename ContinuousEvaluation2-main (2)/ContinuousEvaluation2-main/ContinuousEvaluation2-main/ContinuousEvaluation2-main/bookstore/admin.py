from django.contrib import admin
from .models import Book, Cart, CartItem, Review

admin.site.register(Book)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Review)