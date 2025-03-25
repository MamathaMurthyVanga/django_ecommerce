from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.


def Cart_summary(request):
    # get the cart
    cart = Cart(request)
    cart_products = cart.get_prod
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, "cart_summary.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals})


def Cart_add(request):
    cart = Cart(request)
    # test for post
    if request.POST.get('action') == 'post':
        # get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        # lookup product in DB
        product = get_object_or_404(Product, id=product_id)
        # save to session
        cart.add(product=product, quantity=product_qty)

        # get cart quantity
        cart_quantity = cart.__len__()
        # return response
        # response = JsonResponse({'Product Name: ': product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, ("Product added to cart"))
        return response 


    # efficient code
# def Cart_add(request):
#     cart = Cart(request)

#     if request.POST.get('action') == 'post':
#         product_id = request.POST.get('product_id')

#         # Check if product_id is None or empty
#         if not product_id:
#             return JsonResponse({'error': 'Product ID is missing'}, status=400)

#         try:
#             product_id = int(product_id)  # Convert to int safely
#             product = get_object_or_404(Product, id=product_id)  # Fix 'product' reference
#             cart.add(product=product)
#             return JsonResponse({'Product Name': product.name})
#         except ValueError:
#             return JsonResponse({'error': 'Invalid Product ID'}, status=400)

def Cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        # call delete function in the cart
        cart.delete(product = product_id)
        response = JsonResponse({'product':product_id})
        messages.success(request, ("Product deletd from the cart"))
        return response


def Cart_update(request):
    print("Cart update function called!")
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        # get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty':product_qty})
        messages.success(request, ("Your cart has been updated.."))
        return response
    # return redirect('cart_summary')
    
