from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from app.models import Product, Order,Payment
from app.forms import ProductForm

@staff_member_required
def dashboard(request):
    return render(request, 'custom_admin/dashboard.html')


@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'custom_admin/add_product.html', {'form': form})

@staff_member_required
def manage_orders(request):
    if request.method == 'POST':
        for order_id, order_status in request.POST.items():
            if order_id.startswith('order_status_'):
                order_id = order_id.split('_')[2]
                order = Order.objects.get(id=order_id)
                order.order_state = order_status
                order.save()
        return redirect('admin_manage_orders')
    
    orders = Order.objects.all()
    order_state_choices = Order._meta.get_field('order_state').choices
    return render(request, 'custom_admin/manage_order.html', {'orders': orders, 'order_state_choices': order_state_choices})

@staff_member_required
def delete_order(request,order_id):
    order = get_object_or_404(Order, id= order_id)
    order.delete()
    return redirect('adminmanage_orders  ')



@staff_member_required
def view_payments(request):
    payments = Payment.objects.all().select_related('user')
    return render(request, 'custom_admin/view_payment.html', {'payments': payments})


@staff_member_required
def product_in_market(request):
    products = Product.objects.all()
    return render(request, 'custom_admin/product_in_market.html', {'products': products})

@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin_product_in_market')