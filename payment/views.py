from django.shortcuts import render, redirect
from cart.cart import Cart
from django.contrib import messages

from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from store.models import Product, Profile
import datetime

# import some paypal stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # get the order
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)

        # if request.POST:
        #     status = request.POST['shipping_status']
        #     # check if true or false
        #     if status == 'true':
        #         order = Order.objects.filter(id=pk)
        #         now = datetime.datetime.now()
        #         order.update(shipped = True, shipped_date = now)
        #     else:
        #         order = Order.objects.filter(id=pk)
        #         order.update(shipped = False)
        #     messages.success(request, "shipping status updated")
        #     return redirect('home')


        return render(request, 'payment/orders.html', {"order":order, "items":items})
    else:
        messages.success(request, 'Access Denied')
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)

        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            order.update(shipped = True, shipped_date = now)
  
            messages.success(request, "shipping status updated")
            return redirect('home')


        return render(request, "payment/not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, " Access Denied & not shipped")
        return redirect('home')




def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)

        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            order.update(shipped = False)
  
            messages.success(request, "shipping status updated")
            return redirect('home')
        
        return render(request, "payment/shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "shipped")
        return redirect('home')


def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prod
        quantities = cart.get_quants
        totals = cart.cart_total()

        # get billing info from last page
        payment_form = PaymentForm(request.POST or None)
        # get shipping session data
        my_shipping = request.session.get('my_shipping')


        # gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        # create shipping address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        # create an order 
        if request.user.is_authenticated:
            user = request.user
            # create order
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # add order items
            # get the order id
            order_id = create_order.pk
            # get the product id
            for product in cart_products():
                product_id = product.id
                # get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price 

                # get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user_id=user.id, quantity=value, price=price)
                        create_order_item.save()


            # delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # del the key
                    del request.session[key]


            # delete cart from database(old_cart field)
            current_user = Profile.objects.filter(user__id = request.user.id)
            # delete shopping cart in database (old cart field)
            current_user.update(old_cart = "")



            messages.success(request, "Order placed")
            return redirect('home')
        else:
            # not logged in
            create_order = Order( full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # add order items
            # get the order id
            order_id = create_order.pk
            # get the product id
            for product in cart_products():
                product_id = product.id
                # get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price 

                # get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()

            # delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # del the key
                    del request.session[key]



            messages.success(request, "Order placed")
            return redirect('home')




    else:
        messages.success(request, "Access deined")
        return redirect('home')

   

def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prod
        quantities = cart.get_quants
        totals = cart.cart_total()

        # create a session with shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # get the host
        host = request.get_host()
        # create paypal form 
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': totals,
            'item_name': 'Veg order',
            'no_shipping': '2',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'INR',
            'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
            'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),
        }

        # create acutal paypal button
        paypal_form = PayPalPaymentsForm(initial = paypal_dict)


        # check to see if user is logged in
        if request.user.is_authenticated:
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"paypal_form":paypal_form, "cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})
        else:
            # not logged in
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"paypal_form":paypal_form,"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_info":request.POST, "billing_form":billing_form})

        
        
    else:
        messages.success(request, "Access deined")
        return redirect('home')
    


    



def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prod
    quantities = cart.get_quants
    totals = cart.cart_total()
    if request.user.is_authenticated:
        # checkout as loggedin user
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})
    else:
        # checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, "payment/checkout.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals, "shipping_form":shipping_form})

    



def payment_success(request):
    return render(request, "payment/payment_success.html", {})

def payment_failed(request):
    return render(request, "payment/payment_failed.html", {})