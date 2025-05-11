from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import razorpay
from . models import Cart, Customer, OrderPlaced, Payment, Product, Wishlist
from . forms import CustomerProfileForm, CustomerRegistrationForm
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required 
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.http import HttpResponse
from app.models import Cart, Wishlist
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
import requests



from django.contrib.auth.forms import AuthenticationForm

import requests
from django.shortcuts import render



# Create your views here.

def home(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/home.html", {
        'totalitem': totalitem,
        'wishitem': wishitem,
        'username': request.user.username if request.user.is_authenticated else None
    })


@login_required
def about(request):
    totalitem = 0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/about.html",locals())


@login_required
def contact(request):
    totalitem = 0
    wishitem = 0
    users = []

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))

        # Fetch users from Flask API
        try:
            response = requests.get("http://127.0.0.1:5000/api/users")
            if response.status_code == 200:
                users = response.json()
        except requests.exceptions.RequestException as e:
            print("API Error:", e)

    return render(request, "app/contact.html", {
        "totalitem": totalitem,
        "wishitem": wishitem,
        "users": users
    })

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self,request,val):
        totalitem = 0
        wishitem=0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())

@method_decorator(login_required,name='dispatch')
class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        totalitem = 0
        wishitem=0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"app/category.html",locals())

@method_decorator(login_required,name='dispatch')
class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
        
        totalitem = 0
        wishitem=0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"app/productdetail.html",locals())


import logging
import requests
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerRegistrationForm
from .models import Cart, Wishlist

# Setup logger
logger = logging.getLogger(__name__)

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = Cart.objects.filter(user=request.user).count()
            wishitem = Wishlist.objects.filter(user=request.user).count()
        return render(request, 'app/customerregistration.html', locals())

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            flask_registered = False
            try:
                flask_response = requests.post(
                    'http://127.0.0.1:5000/api/auth/register',
                    json={
                        'username': form.cleaned_data['username'],
                        'email': form.cleaned_data['email'],
                        'password': form.cleaned_data['password1'],
                        'surname': 'Sharma',
                        'city': 'Yamunanagar',
                        'country': 'India'
                    },
                    timeout=5
                )
                if flask_response.status_code == 201:
                    flask_registered = True
            except requests.exceptions.RequestException as e:
                logger.warning(f"Flask backend registration failed: {e}")

            if flask_registered:
                messages.success(request, "Congratulations! User Registered Successfully")
            else:
                messages.warning(request, "User registered in Django, but syncing with backend failed.")
            return redirect('login')
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'app/customerregistration.html', locals())


@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        totalitem = 0
        wishitem=0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulations! Profile Save Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request, 'app/profile.html',locals())

@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/address.html',locals())

@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem = 0
        wishitem=0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations! Profile Update Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")

@login_required
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")

@login_required
def adminn(request):
    totalitem = 0
    wishitem = 0
    users = []
    selected_user = None
    selected_user_cart = []

    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
        # Fetch users from Flask API
        try:
            response = requests.get("http://127.0.0.1:5000/api/users")
            if response.status_code == 200:
                users = response.json()
                # Get selected user from request
                selected_user_id = request.GET.get('user_id')
                if selected_user_id:
                    selected_user = next((user for user in users if user['id'] == int(selected_user_id)), None)
                    if selected_user:
                        try:
                            cart_response = requests.get(f"http://127.0.0.1:5000/api/cart/user/{selected_user_id}")
                            if cart_response.status_code == 200:
                                selected_user_cart = cart_response.json()
                        except Exception as e:
                            selected_user_cart = []
        except Exception as e:
            users = []

    return render(request, "app/adminn.html", {
        "totalitem": totalitem,
        "wishitem": wishitem,
        "users": users,
        "selected_user": selected_user,
        "selected_user_cart": selected_user_cart
    })


@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    totalitem = 0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/addtocart.html',locals())

@login_required
def show_wishlist(request):
    user = request.user
    totalitem = 0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    product = Wishlist.objects.filter(user=user)
    return render(request,"app/wishlist.html",locals())
    
@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self,request):
        totalitem = 0
        wishitem=0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        user=request.user 
        add=Customer.objects.filter(user=user) 
        cart_items=Cart.objects.filter(user=user)  
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = { "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
        payment_response = client.order.create(data=data)
        print(payment_response)
        #{'id': 'order_KU0n5eKcEeiLOm', 'entity': 'order', 'amount': 14500, 'amount_paid': 0, 'amount_due': 14500, 'currency': 'INR', 'receipt': 'order_rcptid_12', 'offer_id': None, 'status': 'created', 'attempts': 0, 'notes': [], 'created_at': 1665829122}
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
             payment = Payment(
                 user=user,
                 amount=totalamount,
                 razorpay_order_id=order_id,
                 razorpay_payment_status = order_status
             )
             payment.save()
        return render(request, 'app/checkout.html',locals())

@login_required
def payment_done(request):
    order_id=request.GET.get('order_id') 
    payment_id=request.GET.get('payment_id') 
    cust_id=request.GET.get('cust_id') 
    #print("payment_done : oid = ",order_id," pid = ",payment_id," cid = ",cust_id)
    user=request.user 
    #return redirect("orders")
    customer=Customer.objects.get(id=cust_id)
    #To update payment status and payment id
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    #To save order details
    cart=Cart.objects.filter(user=user) 
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()
    return redirect("orders")

@login_required
def orders(request):
    totalitem = 0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    order_placed=OrderPlaced.objects.filter(user=request.user) 
    return render(request, 'app/orders.html',locals())

def plus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

def plus_wishlist(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully',
        }
        return JsonResponse(data)

def minus_wishlist(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        product=Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data={
            'message':'Wishlist Remove Successfully',
        }
        return JsonResponse(data)

@login_required
def search(request):
    query = request.GET['search']
    totalitem = 0
    wishitem=0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request,"app/search.html",locals())


# Custom Login View
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})

# Custom Logout View
def custom_logout(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'Goodbye, {username}!')
    return redirect('home')

@login_required
def dashboard(request):
    """Dashboard view that displays users and cart items"""
    try:
        # Get API key
        api_key = api_client.get_api_key(request.user.username, request.user.password)
        if not api_key:
            messages.error(request, 'Failed to authenticate with API')
            return redirect('login')

        # Get users and cart items
        users = api_client.get_users()
        cart_items = api_client.get_cart_items()

        context = {
            'users': users,
            'cart_items': cart_items,
            'api_key': api_key
        }
        return render(request, 'app/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('login')

@login_required
def user_list(request):
    """View for listing and managing users"""
    try:
        users = api_client.get_users()
        return render(request, 'app/user_list.html', {'users': users})
    except Exception as e:
        messages.error(request, f'Error loading users: {str(e)}')
        return redirect('dashboard')

@login_required
def create_user(request):
    """View for creating a new user"""
    if request.method == 'POST':
        try:
            user_data = {
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'password': request.POST.get('password'),
                'city': request.POST.get('city'),
                'country': request.POST.get('country')
            }
            new_user = api_client.create_user(user_data)
            if new_user:
                messages.success(request, 'User created successfully')
            else:
                messages.error(request, 'Failed to create user')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    return redirect('user_list')

@login_required
def update_user(request, user_id):
    """Update Django User model's name and email via AJAX from adminn modal."""
    import json
    if request.method == 'POST':
        try:
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
                name = data.get('name', '').strip()
                email = data.get('email', '').strip()
                user = User.objects.get(pk=user_id)
                user.first_name = name
                user.email = email
                user.save()
                return JsonResponse({'success': True})
            else:
                name = request.POST.get('name', '').strip()
                email = request.POST.get('email', '').strip()
                user = User.objects.get(pk=user_id)
                user.first_name = name
                user.email = email
                user.save()
                messages.success(request, 'User updated successfully')
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f'Error updating user: {str(e)}')
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    return redirect('user_list')

@login_required
def delete_user(request, user_id):
    """View for deleting a user"""
    try:
        if api_client.delete_user(user_id):
            messages.success(request, 'User deleted successfully')
        else:
            messages.error(request, 'Failed to delete user')
    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
    return redirect('adminn')

@login_required
def cart_list(request):
    """View for listing and managing cart items"""
    try:
        cart_items = api_client.get_cart_items()
        return render(request, 'app/cart_list.html', {'cart_items': cart_items})
    except Exception as e:
        messages.error(request, f'Error loading cart items: {str(e)}')
        return redirect('dashboard')

@login_required
def create_cart_item(request):
    """View for creating a new cart item"""
    if request.method == 'POST':
        try:
            item_data = {
                'product_name': request.POST.get('product_name'),
                'price': float(request.POST.get('price')),
                'quantity': int(request.POST.get('quantity'))
            }
            new_item = api_client.create_cart_item(item_data)
            if new_item:
                messages.success(request, 'Cart item created successfully')
            else:
                messages.error(request, 'Failed to create cart item')
        except Exception as e:
            messages.error(request, f'Error creating cart item: {str(e)}')
    return redirect('cart_list')

@login_required
def update_cart_item(request, item_id):
    """View for updating a cart item"""
    if request.method == 'POST':
        try:
            item_data = {
                'product_name': request.POST.get('product_name'),
                'price': float(request.POST.get('price')),
                'quantity': int(request.POST.get('quantity'))
            }
            updated_item = api_client.update_cart_item(item_id, item_data)
            if updated_item:
                messages.success(request, 'Cart item updated successfully')
            else:
                messages.error(request, 'Failed to update cart item')
        except Exception as e:
            messages.error(request, f'Error updating cart item: {str(e)}')
    return redirect('cart_list')

@login_required
def delete_cart_item(request, item_id):
    """View for deleting a cart item"""
    try:
        if api_client.delete_cart_item(item_id):
            messages.success(request, 'Cart item deleted successfully')
        else:
            messages.error(request, 'Failed to delete cart item')
    except Exception as e:
        messages.error(request, f'Error deleting cart item: {str(e)}')
    return redirect('cart_list')

@login_required
def search(request):
    """View for searching users and cart items"""
    query = request.GET.get('query', '')
    try:
        results = api_client.search(query)
        return JsonResponse(results)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


