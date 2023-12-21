from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .forms import UserRegisterForm, MasterRegisterForm, CaptainRegisterForm
from kanyarasi.models import UserProfile
from django.contrib import messages
from .forms import MenuItemForm
from kanyarasi.models import MenuItem
from .models import Master
from .models import MenuItem, Master, Order, CompletedOrder
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import random
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseNotAllowed
from django.urls import reverse
from django.shortcuts import get_object_or_404



def home(request):
  return render(request, 'home.html')  # Make sure you have a template named 'home.html'
def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful')
            UserProfile.objects.create(user=user, role='user')
            return redirect('user_login')  # Redirect to user dashboard
    else:
        form = UserRegisterForm()
    return render(request, 'user_register.html', {'form': form})


def master_register(request):
    if request.method == 'POST':
        form = MasterRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            messages.success(request, 'Registration successful')
            UserProfile.objects.create(user=user, role='master')
            return redirect('master_login')
    else:
        form = MasterRegisterForm()
    return render(request, 'master_register.html', {'form': form})


def captain_register(request):
    if request.method == 'POST':
        form = CaptainRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            messages.success(request, 'Registration successful')  
            UserProfile.objects.create(user=user, role='captain')  
            return redirect('captain_login') 
    else:
        form = CaptainRegisterForm()
    return render(request, 'captain_register.html', {'form': form})


def user_login(request):
  if request.method == 'POST':
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(request, username=username, password=password)
      if user:
          login(request, user)
          return redirect('user_dash')
      else:
          return render(request, 'user_login.html', {'error_message': 'Invalid login'})
  return render(request, 'user_login.html')

def master_login(request):
  if request.method == 'POST':
      # Extract credentials and authenticate
      username = request.POST.get('username')
      password = request.POST.get('password')
      user = authenticate(request, username=username, password=password)
      if user is not None:
          login(request, user)
          return redirect('master_dash')
      else:
          return render(request, 'master_login.html', {'error': 'Invalid username or password'})

  # For a GET request, or if the POST login failed
  return render(request, 'master_login.html')

def captain_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and UserProfile.objects.filter(user=user, role='captain').exists():
            login(request, user)
            return redirect('cap_dash')
        else:
          return render(request, 'captain_login.html')
    return render(request, 'captain_login.html')
  

def add_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                master_profile = Master.objects.get(user=request.user)
            except ObjectDoesNotExist:
                messages.error(request, "No Master profile found for this user.")
                return redirect('add_item')

            menu_item = form.save(commit=False)
            menu_item.master = master_profile
            menu_item.save()
            messages.success(request, "Menu item added successfully.")
            return redirect('view_menu')
    else:
        form = MenuItemForm()

    return render(request, 'add_item.html', {'form': form})



def view_menu(request):
    if request.user.is_authenticated:
        try:
            master_profile = Master.objects.get(user=request.user)
            menu_items = MenuItem.objects.filter(master=master_profile)
        except ObjectDoesNotExist:
            menu_items = []
    else:
        menu_items = []

    return render(request, 'view_menu.html', {'menu_items': menu_items})



def master_dash(request):
  return render(request, 'master_dash.html')

def cap_dash(request):
  return render(request, 'cap_dash.html')

#def user_dash(request):
  # Get all masters
 # masters = Master.objects.prefetch_related('menuitem_set').all()
 # return render(request, 'user_dash.html', {'masters': masters})

@login_required
def user_dash(request):
    masters = Master.objects.all()
    return render(request, 'user_dash.html', {'masters': masters})

@login_required
def order_status(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'order_status.html', {'orders': orders})

@login_required
def cart_view(request):
    cart_item_ids = request.session.get('cart', [])
    cart_items = MenuItem.objects.filter(id__in=cart_item_ids)
    total_amount = sum(item.price for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })



@login_required
@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('itemId')
            if item_id:
                cart = request.session.get('cart', [])
                cart.append(item_id)
                request.session['cart'] = cart
                return JsonResponse({'status': 'success', 'message': 'Item added to cart'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Item ID not provided'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@login_required
def cart_view(request):
    cart_item_ids = request.session.get('cart', [])
    cart_items_with_details = [{
        'name': item.name,
        'price': item.price,
        'image_url': item.image_url  # Assuming your model has an image_url field
    } for item_id in cart_item_ids for item in MenuItem.objects.filter(id=item_id)]
    total_amount = sum(item['price'] for item in cart_items_with_details)
    return render(request, 'cart.html', {
        'cart_items': cart_items_with_details,
        'total_amount': total_amount
    })


@login_required
def get_cart_items(request):
    cart_item_ids = request.session.get('cart', [])
    cart_items = MenuItem.objects.filter(id__in=cart_item_ids).values('name', 'price')
    return JsonResponse({'items': list(cart_items)})


@login_required
@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_index = data.get('itemIndex')
            if item_index is not None:
                cart = request.session.get('cart', [])
                if 0 <= int(item_index) < len(cart):
                    cart.pop(int(item_index))
                request.session['cart'] = cart
                return JsonResponse({'status': 'success', 'message': 'Item removed from cart'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Item index not provided'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)





@login_required
def submit_order(request):
    if request.method == 'POST':
        cart_item_ids = request.session.get('cart', [])
        cart_items_with_details = get_cart_items_with_details(request.user, cart_item_ids)
        total_amount = sum(item['price'] for item in cart_items_with_details)

        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        phone_number = request.POST.get('phone_number')
        pincode = request.POST.get('pincode')
        tracking_number = random.randint(10000, 99999)

        order = Order(
            user=request.user,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            phone_number=phone_number,
            pincode=pincode,
            tracking_number=str(tracking_number),
            status='pending'  # Set the status to 'pending'
        )
        order.save()

        for item_details in cart_items_with_details:
            item = MenuItem.objects.get(id=item_details['id'])
            order.items.add(item)

        order.save()
        request.session['cart'] = []

        return render(request, 'submit_order.html', {
            'cart_items': cart_items_with_details,
            'total_amount': total_amount,
            'address_line_1': address_line_1,
            'address_line_2': address_line_2,
            'phone_number': phone_number,
            'pincode': pincode,
            'tracking_number': tracking_number,
        })
    else:
        return redirect('cart_view')


def get_cart_items_with_details(user, cart_item_ids):
    items_with_details = []
    for item_id in cart_item_ids:
        item = MenuItem.objects.get(id=item_id)
        image_url = item.image.url if item.image and hasattr(item.image, 'url') else None
        items_with_details.append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'image_url': image_url
        })
    return items_with_details


@login_required
def view_order(request):
    try:
        master_profile = Master.objects.get(user=request.user)
        # Filter orders to show only those with 'pending' status
        pending_orders = Order.objects.filter(items__master=master_profile, status='pending').distinct()
        return render(request, 'view_order.html', {'orders': pending_orders})
    except Master.DoesNotExist:
        # Handle the case where the master profile is not found
        return render(request, 'view_order.html', {'error': 'Master profile not found'})


@login_required
def cancel_order(request):
    if request.method == 'POST':
        order_id = request.GET.get('order_id')
        try:
            order = Order.objects.get(id=order_id)
            # Logic to cancel the order
            order.delete()  # or any other logic you have for canceling
            return JsonResponse({'status': 'success', 'message': 'Order cancelled successfully'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def complete_order_page(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        return render(request, 'complete_order.html', {'order': order})
    except Order.DoesNotExist:
        return HttpResponseNotFound('<h1>Order not found</h1>')
    
@login_required
def confirm_complete_order(request, order_id):
    if request.method == 'POST':
        try:
            # Retrieving the order by ID only as it should be unique
            order = Order.objects.get(id=order_id)
            
            # Check if the order's items are associated with the master
            if not order.items.filter(master=request.user.master).exists():
                messages.error(request, "You do not have permission to complete this order.")
                return redirect('view_order')

            # Update the order status
            order.status = 'completed'
            order.save()
            messages.success(request, f'Order {order_id} marked as complete.')
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
        except Order.MultipleObjectsReturned:
            messages.error(request, f'Multiple orders found with ID {order_id}.')

        return redirect('view_order')
    else:
        return HttpResponseNotAllowed(['POST'])



'''@login_required
def complete_order(request, order_id):
    try:
        print("Completing order:", order_id)

        # Assuming order_id is a path parameter
        order = Order.objects.get(id=order_id)
        order.status = 'completed'
        order.save()

        print(f"Order {order_id} marked as complete.")
        return JsonResponse({'status': 'success', 'message': f'Order {order_id} marked as complete.'})
    except Exception as e:
        print("Error in completing order:", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)'''



@login_required
def cap_dash(request):
    completed_orders = Order.objects.filter(status='completed')
    return render(request, 'cap_dash.html', {'orders': completed_orders})

@login_required
def deliver_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'deliver_order.html', {'order': order})


@login_required
@require_POST
def mark_order_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'delivered'
    order.save()
    return redirect('cap_dash')

@login_required
def order_status(request):
    delivered_orders = Order.objects.filter(user=request.user, status='delivered')
    return render(request, 'order_status.html', {'delivered_orders': delivered_orders})

@login_required
def delete_order(request, order_id):
    order_to_delete = Order.objects.filter(id=order_id, user=request.user)
    if order_to_delete.exists():
        order_to_delete.delete()
    return redirect('order_status')