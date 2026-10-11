from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Category, MenuItem, Table, Order
from .forms import CategoryForm, MenuItemForm, TableForm,OrderForm, OrderItemFormSet
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

def category_list(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'orders/category_list.html', context)

def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New food category added successfully!")
            return redirect('menu_list')  # Or wherever you want to redirect after creation
    else:
        form = CategoryForm()
        
    context = {'form': form}
    return render(request, 'orders/category_form.html', context)

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated successfully!")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'orders/category_form.html', {'form': form, 'category': category})

def category_delete(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted successfully!")
    return redirect('category_list')

def menu_list(request):
    categories = Category.objects.all()
    menu_items = MenuItem.objects.select_related('category').all()
    
    category_id = request.GET.get('category')
    if category_id:
        menu_items = menu_items.filter(category_id=category_id)

    return render(request, 'orders/menu_list.html', {
        'categories': categories,
        'menu_items': menu_items,
        'selected_category': category_id,
    })


def menu_item_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item added successfully!")
            return redirect('menu_list')
    else:
        form = MenuItemForm()
    return render(request, 'orders/menu_form.html', {'form': form, 'title': 'Add Menu Item'})


def menu_item_update(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item updated successfully!")
            return redirect('menu_list')
    else:
        form = MenuItemForm(instance=item)
    return render(request, 'orders/menu_form.html', {'form': form, 'title': 'Edit Menu Item'})

def menu_delete_view(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
   
    item_name = item.name
    item.delete()
    
    messages.success(request, f"Menu item '{item_name}' was successfully deleted.")
    return redirect('menu_list')

def table_list(request):
    tables = Table.objects.all()
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Table added successfully!")
            return redirect('table_list')
    else:
        form = TableForm()

    return render(request, 'orders/table_list.html', {
        'tables': tables,
        'form': form,
    })

def table_management(request, pk=None):
    table_instance = get_object_or_404(Table, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table_instance)
        if form.is_valid():
            form.save()
            action = "updated" if pk else "added"
            messages.success(request, f"Table successfully {action}!")
            return redirect('table_list')
    else:
        form = TableForm(instance=table_instance)
        
    tables = Table.objects.all().order_by('table_number')
    
    context = {
        'tables': tables,
        'form': form,
        'editing_table': table_instance,
    }
    return render(request, 'orders/table_list.html', context)

def table_delete(request, pk):
    if request.method == 'POST':
        table = get_object_or_404(Table, pk=pk)
        num = table.table_number
        table.delete()
        messages.success(request, f"Table #{num} deleted successfully!")
    return redirect('table_list')

def order_create(request):
    
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = order_form.save(commit=False)
                
                if request.user.is_authenticated:
                    order.server = request.user
               
                if order.table:
                    table = Table.objects.select_for_update().get(pk=order.table.pk)
                    
                    if table.available_seats < order.party_size:
                        messages.error(
                            request, 
                            f"Table {table.table_number} only has {table.available_seats} seats available, but {order.party_size} were requested!"
                        )
                        return render(request, 'orders/order_create.html', {
                            'order_form': order_form,
                            'formset': formset,
                        })
                  
                    table.current_occupancy += order.party_size
                    table.update_occupancy_status()

                order.save()

                items = formset.save(commit=False)
                for item in items:
                    item.order = order
                    item.unit_price = item.menu_item.price
                    item.save()

                for deleted_item in formset.deleted_objects:
                    deleted_item.delete()

                order.calculate_totals()

            messages.success(request, f"Order #{order.id} created successfully!")
            return redirect('order_detail', pk=order.id)
    else:
        order_form = OrderForm()
        formset = OrderItemFormSet()

    context = {
        'order_form': order_form,
        'formset': formset,
    }

    return render(request, 'orders/order_create.html', context)

def kitchen_display(request):
   
    active_orders = Order.objects.filter(
        status__in=['PENDING', 'PREPARING', 'READY','SERVED']
    ).prefetch_related('items__menu_item').select_related('table').order_by('created_at')

    return render(request, 'orders/kitchen_display.html', {
        'orders': active_orders,
    })


def update_order_status(request, pk, new_status):
    order = get_object_or_404(Order, pk=pk)
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]

    if new_status in valid_statuses:
        if new_status == 'CANCELLED' :
            if order.status in ['READY', 'SERVED', 'PAID']:
                messages.error(request, f"Cannot cancel Order #{order.id} because it has already progressed past preparation.")
                return redirect('order_detail', pk=order.id)

        if new_status == 'PAID' and order.status not in ['READY', 'SERVED']:
            messages.error(request, f"Order #{order.id} cannot be paid because it has not been prepared and served yet!")
            return redirect('order_detail', pk=order.id)
        
        with transaction.atomic():
            order.status = new_status
            order.save()

            if new_status in ['PAID','CANCELLED'] and order.table:
                table = order.table
                table.current_occupancy = max(0, table.current_occupancy - order.party_size)
                table.update_occupancy_status()  

        messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
    else:
        messages.error(request, "Invalid status update requested.")

    if new_status == 'SERVED':
        return redirect('order_detail', pk=order.id)

    if 'kitchen' in request.META.get('HTTP_REFERER', ''):
        return redirect('kitchen_display')
    
    return redirect('order_detail', pk=order.id)

def order_history(request):
    completed_orders = Order.objects.filter(
        status__in=['SERVED', 'PAID', 'CANCELLED']
    ).select_related('table', 'server').order_by('-updated_at')

    return render(request, 'orders/order_history.html', {
        'orders': completed_orders,
    })

def order_detail(request, pk):
   
    order = get_object_or_404(
        Order.objects.select_related('table', 'server').prefetch_related('items__menu_item'),
        pk=pk
    )

    return render(request, 'orders/order_details.html', {
        'order': order,
    })

def dashboard(request):
    
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)

    today_paid_orders = Order.objects.filter(status='PAID', created_at__date=today)
    total_sales = sum(order.grand_total for order in today_paid_orders)

    pending_count = Order.objects.filter(status='PENDING').count()
    preparing_count = Order.objects.filter(status='PREPARING').count()
    ready_count = Order.objects.filter(status='READY').count()

    # 2. Active Kitchen Orders (Pending, Preparing, or Ready)
    active_orders_count = Order.objects.filter(status__in=['PENDING', 'PREPARING', 'READY']).count()

    # 3. Table Occupancy (Occupied/Full tables vs Total tables)
    total_tables_count = Table.objects.count()
    occupied_tables_count = Table.objects.exclude(status='AVAILABLE').count()

    # 4. Completed Orders Today (Paid or Served)
    completed_orders_count = Order.objects.filter(status__in=['SERVED', 'PAID'], created_at__date=today).count()

    # 5. Recent Orders List for the table
    recent_orders = Order.objects.all().order_by('-created_at')[:10]

    context = {
        'total_sales': round(total_sales, 2),
        'active_orders_count': active_orders_count,
        'occupied_tables_count': occupied_tables_count,
        'total_tables_count': total_tables_count,
        'completed_orders_count': completed_orders_count,
        'pending_count': pending_count,
        'preparing_count': preparing_count,
        'ready_count': ready_count,
        'recent_orders': recent_orders,
    }

    return render(request, 'orders/dashboard.html', context)