from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index, name='bookstore_index'),
    path('cards/', views.cards, name='cards'),
    path('cart1/', views.cart1, name='cart1'),
    path('display/', views.display, name='display'),
    path('feedback/', views.feedback, name='feedback'),
    
    
    path('', views.index, name='index'),
   
    # path('register/', views.register, name='register'),
]