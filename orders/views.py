from django.shortcuts import render , redirect
#from .forms orderForm

from carts.models import CartItem
from .forms import OrderForm
from .models import Order , OrderProduct , Payment
from store.models import Product

#Para mensajes succes o errors
from django.contrib import messages 

#Para enviar mensajes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


#tiempo
from datetime import  date

#PAYPAL
from paypal.standard.forms import PayPalPaymentsForm

from django.conf import settings
from django.urls import reverse

# Create your views here.

def place_order(request,total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('store')
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2*total)/100
    grand_total = total + tax


    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.user = request.user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line1 = form.cleaned_data['address_line1']
            data.address_line2 = form.cleaned_data['address_line2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            current_date = date.today()
            current_date_str = current_date.strftime("%Y%m%d")
            #20280110
            order_number = f"{current_date_str}{data.id}"
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            
            product_names = []
            for cart_item in cart_items:
                product_names.append(cart_item.product.product_name)

            # Unir los nombres de los productos en una sola cadena separada por comas
            item_name = ', '.join(product_names)
            host = request.get_host()
            return_url = reverse('payments')
            # Agrega el parámetro de consulta 'order_number'
            return_url = f'{return_url}?order_number={order_number}'
            paypal_checkout = {
                'business':settings.PAYPAL_RECEIVER_EMAIL,
                'amount': grand_total,
                'item_name':item_name,
                'invoice': data.order_number,
                'tax' : tax,
                'currency_code': 'USD',
                'time_created':current_date,
                'payment_date': order_number,
                'notify_url': f"http://{host}{reverse('paypal-ipn')}",
                "return": request.build_absolute_uri(return_url),  # La URL a la que PayPal redirigirá después del pago exitoso.
                "cancel_return": request.build_absolute_uri(reverse('checkout')),  # La URL a la que PayPal redirigirá si el usuario cancela el pago.
                
            }
            paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total': total,
                'tax': tax,
                'grand_total':grand_total,
                'paypal': paypal_payment,
                'order_number': order_number,
            }
            return render(request,'orders/payments.html', context)
    else:
        return redirect('checkout')
def payments(request):
    payer_id = request.GET.get('PayerID')
    current_user = request.user
    order_number = request.GET.get('order_number')
    if payer_id and order_number:
        order = Order.objects.get(user=current_user, order_number=order_number)
        payment_method='paypal'
        payment = Payment(
            user=current_user,
            payment_id=order.order_number,
            payment_method=payment_method,
            amount_id=order.order_total,
            status=order.status,
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            order_product = OrderProduct(
                order=order,  
                payment=payment,
                user=current_user,  
                product=item.product, 
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )
        order_product.save()
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()
        CartItem.objects.filter(user=current_user).delete()

        if Payment.objects.filter(user=request.user).exists():
            mail_subject = 'Gracias por la compra'
            body = render_to_string('orders/order_recieved_email.html',{
                        'user': request.user,
                        'order': order,
                    })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, body, to=[to_email])
            send_email.send()   
        return_url = reverse('order_complete')  # Asume que tu vista se llama 'order_complete'
        return_url = f'{return_url}?order_number={order_number}&PayerID={payer_id}'  # Agrega los parámetros
        return redirect(return_url)

    else:
        return redirect('store')
    

def order_complete(request):
    order_number = request.GET.get('order_number')
    payer_id = request.GET.get('PayerID')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)
        
        subtotal= 0
        for i in ordered_products:
            subtotal += i.product_price*i.quantity

        payment = Payment.objects.get(payment_id =order_number, )
        order.status = 'Cancelado'
        order.save()
        context= {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'payer_id':payer_id,
            'payment':payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return render(request, 'orders/order_complete.html')

def pruebas(request,order_number):
    current_user = request.user
    #order_products = OrderProduct.objects.get(user=current_user,payment=20230921258) 
    #payments = Payment.objects.get(payment_id=order_number)
    orders = Order.objects.get(user=request.user, order_number=order_number)
    #order_number =order_products.order.order_number

    context = {
         #'order_n':total,
         #'pay_id':payment_id,
         #'pay1':order_products.order.order_number,
    }
    return render(request,'pruebas.html', context)
