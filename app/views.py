from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse,JsonResponse
from django.views import View
from .models import Product,Customer,WishlistItem,CartItem,STATES,SIZE_CHOICES,Order,generate_order_id,ORDER_STATES,Payment
from .forms import CustomerRegistrationForm,Customerprofileform,ChangePasswordForm,OrderForm
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay
from django.urls import reverse
import json


def home(request):
    return render(request, 'app/home.html')

def category(request, val):
    if request.method == "GET":
        products = Product.objects.filter(category=val)
        return render(request, "app/category.html", {'products': products, 'category': val})

def product_detail(request, product_id):
    if request.method == "GET":
        product = get_object_or_404(Product, pk=product_id)
        return render(request, "app/productdetails.html", {'product': product})

def about(request):
    return render(request,'app/about.html')

def contact(request):
    return render(request,'app/contact.html')

@login_required(login_url='login')
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'SIZE_CHOICES': SIZE_CHOICES,
    }
    return render(request, 'app/cart.html', context)

@login_required(login_url='login')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        size = request.POST.get('size', 'M')  # Default to 'M' if not provided
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            size=size  # Ensure size is used in the get_or_create
        )
        if not created:
            cart_item.quantity += 1  # Assuming a method to increase quantity
            cart_item.save()
        messages.success(request, 'Item added to cart successfully.')
        return redirect('cart')
    else:
        messages.error(request, 'Failed to add item to cart.')
        return redirect('cart')

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart successfully.')
    return redirect('cart')

class UpdateSizeView(View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        size = request.POST.get('size')
        if size in dict(SIZE_CHOICES):
            cart_item.size = size
            cart_item.save()
            messages.success(request, 'Size updated successfully.')
        else:
            messages.error(request, 'Invalid size selected.')
        return redirect('cart')

@login_required(login_url='login')
def adjust_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.POST.get('action')
    
    if action == 'increase':
        cart_item.increase_quantity()
    elif action == 'decrease':
        cart_item.decrease_quantity()

    cart_item.save()
    return redirect('cart')


@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    total_price = sum(item.get_item_price() for item in wishlist_items)
    context = {
        'wishlist_items': wishlist_items,
        'total_price': total_price
    }
    return render(request, "app/wishlist.html", context)


@login_required(login_url='login')
def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist_item.quantity += 1
            wishlist_item.save()
        messages.success(request, 'Item added to wishlist successfully.')
        return redirect('wishlist')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('wishlist')

class RemoveFromWishlist(View):
    def post(self, request, item_id):
        wishlist_item = get_object_or_404(WishlistItem, id=item_id)
        if wishlist_item.user == request.user:
            wishlist_item.delete()
        return redirect('wishlist')


class WishlistToCart(View):
    def post(self, request):
        wishlist_items = WishlistItem.objects.filter(user=request.user)
        for item in wishlist_items:
            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=item.product)
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()
            item.delete()
        return redirect('cart')

class RegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/signup.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save(commit=False)  # Get user instance without saving to DB yet
            user.set_password(form.cleaned_data['password1'])  # Set password with hashed value
            user.save()  # Now save the user to DB

            # Authenticate and log in the user
            user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                # Redirect to the home page
                return redirect('home')
            else:
                messages.error(request, 'Failed to authenticate the user. Please contact support.')
        else:
            # If form is invalid, display errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        # If form is invalid or authentication fails, render the registration form again
        return render(request, 'app/signup.html', {'form': form})

    
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login the user
            login(request, user)
            messages.success(request, f"Hey {username}! welcome to WESELL.")
            return redirect('home')  # Redirect to home page after successful login
        else:
            # Authentication failed
            messages.error(request, "Incorrect password or username. Please try again.")
            return redirect('login')  # Redirect back to login page after failed login attempt
    else:
        # Render login page for GET request
        return render(request, 'app/login.html', {})
    

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

class ProfileView(View):
    def get(self, request):
        # Check if the user already has a profile
        try:
            customer = Customer.objects.get(user=request.user)
            # If the user has a profile, display the profile data
            form = Customerprofileform(instance=customer)
            context = {'form': form, 'customer': customer}
        except Customer.DoesNotExist:
            # If the user doesn't have a profile, display an empty form
            form = Customerprofileform()
            context = {'form': form}

        return render(request, 'app/customerprofile.html', context)

    def post(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
            form = Customerprofileform(request.POST, instance=customer)
        except Customer.DoesNotExist:
            form = Customerprofileform(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'app/customerprofile.html', {'form': form})

@login_required
def edit_profile(request, customer_id):
    if request.method == "POST":
        customer = Customer.objects.get(pk=customer_id)
        form = Customerprofileform(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated!")
            return redirect('profile')  # Redirect to the user's profile page after updating
    else:
        customer = Customer.objects.get(pk=customer_id)
        form = Customerprofileform(instance=customer)
    return render(request, 'app/edit_profile.html', {'form': form})


# def order(request):
#     return render(request,'app/order.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            
            # Get the current user
            user = request.user
            
            # Check if the old password is correct
            if not user.check_password(old_password):
                messages.error(request, 'Your old password is incorrect.')
                return redirect('change_password')

            # Check if the new password and confirm password match
            if new_password != confirm_password:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect('change_password')

            # Change the password
            user.set_password(new_password)
            user.save()

            # Update the user's session to prevent logout
            update_session_auth_hash(request, user)

            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ChangePasswordForm()
    return render(request, 'app/change_password.html', {'form': form})
  


def payment_success(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        razorpay_payment_id = data['razorpay_payment_id']
        razorpay_order_id = data['razorpay_order_id']
        razorpay_signature = data['razorpay_signature']

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.paid = True
            payment.razorpay_payment_status = 'success'
            payment.save()

            # Now that payment is successful, update the order status
            order = Order.objects.get(order_id=payment.order_id)
            order.order_state = 'Success'
            order.save()

            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'failure'}, status=400)

    return JsonResponse({'status': 'failure'}, status=400)

@login_required(login_url='login')
@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            cart_items = CartItem.objects.filter(user=request.user)
            grand_total = sum(item.total_price() for item in cart_items) + 80

            if cart_items.exists():
                order_id = generate_order_id()
                mode_of_payment = form.cleaned_data['mode_of_payment']

                for cart_item in cart_items:
                    order = Order.objects.create(
                        user=request.user,
                        order_id=order_id,
                        product=cart_item.product,
                        size=cart_item.size,
                        quantity=cart_item.quantity,
                        total_amount=cart_item.total_price() + 80,
                        order_state='Pending',  # Order state is set to pending initially
                        number=form.cleaned_data['number'],
                        address=form.cleaned_data['address'],
                        pincode=form.cleaned_data['pincode'],
                        state=form.cleaned_data['state'],
                        mode_of_payment=mode_of_payment
                    )

                if mode_of_payment == 'Online':
                    # Create Razorpay Order
                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                    razorpay_order = client.order.create(dict(amount=int(grand_total * 100), currency='INR', payment_capture='1'))

                    # Save Payment details
                    payment = Payment.objects.create(
                        user=request.user,
                        amount=grand_total,
                        razorpay_order_id=razorpay_order['id'],
                        razorpay_payment_status='Pending',
                    )

                    cart_items.delete()
                    return render(request, 'app/payment.html', context={'razorpay_order_id': razorpay_order['id'], 'grand_total': grand_total, 'user': request.user, 'amount_in_paise': int(grand_total * 100), 'razorpay_key_id': settings.RAZORPAY_KEY_ID})

                cart_items.delete()
                return redirect('orders')  # Redirect to orders page or success page for COD
            else:
                return HttpResponse("Your cart is empty.")
    else:
        form = OrderForm()

    cart_items = CartItem.objects.filter(user=request.user)
    grand_total = sum(item.total_price() for item in cart_items) + 80

    return render(request, 'app/checkout.html', {'form': form, 'cart_items': cart_items, 'grand_total': grand_total})

@login_required
def order_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'app/order.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    try:
        # Fetch the order, or return a 404 error if not found
        order = get_object_or_404(Order, id=order_id)

        # Check if the request user is the owner of the order
        if order.user != request.user:
            messages.error(request, 'You are not authorized to cancel this order.')
            return redirect('orders')

        # Check if the order is already shipped
        if order.order_state in ['Shipped','Out for Delivery','Delivered','Returned']:
            messages.error(request, 'The product is already shipped and cannot be canceled.')
        elif order.order_state == 'Cancelled':
            messages.error('This product is already Cancelled.')
        else:
            order.order_state = 'Cancelled'
            order.save()
            messages.success(request, 'Order canceled successfully.')

    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
    except Exception as e:
        messages.error(request, 'Something went wrong. Please try again!')

    return redirect('orders')

def search(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(title__icontains=query)

    return render(request, 'app/search.html', {'results': results, 'query': query})





