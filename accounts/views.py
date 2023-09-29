from django.shortcuts import render , redirect , get_object_or_404
from django.urls import reverse

from orders.models import Order
from .forms import RegistrationForm, UserProfileForm, UserForm
from .models import Account , UserProfile
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage


#para conectar con mi app Carts
from carts.models import Cart, CartItem
from carts.views import _cart_id 

#importando forms
import requests



# Create your views here.
def register(request):
    form = RegistrationForm()

    if request.method =='POST':
        form = RegistrationForm(request.POST) 
        if form.is_valid():
            first_name   = form.cleaned_data['first_name']
            last_name   = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            #ASasAS@GMAIL.COM
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name,email=email,password=password,username=username)
            user.phone_number =phone_number
            user.save()

            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()



            current_site = get_current_site(request)
            mail_subject = 'Activa tu cuenta'
            body = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })

            to_email = email
            
            send_email = EmailMessage(mail_subject,body, to=[to_email])
            send_email.send()

            #messages.success(request,'Se registro el usuario correctamente')
            return redirect('/accounts/login/?command=verification&email='+email)

    context = {
        'form': form
    }
    return render(request,'accounts/register.html', context)


def login(request):

    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password= password)

        if user is not None:
            try: 
                cart = Cart.objects.get(cart_id=_cart_id(request))

                is_cart_item_exists= CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists: #si es true el carrito no esta vacio y tiene elementos


                    cart_items = CartItem.objects.filter(cart=cart)

                    # Obtener las variaciones de los productos en el carrito del usuario autenticado
                    product_variation = [
                    list(item.variations.all()) for item in cart_items
                    ]

                    # Obtener los elementos del carrito del usuario actual (que podría ser el carrito sin autenticar)
                    user_cart_items = CartItem.objects.filter(user=user)

                    # Obtener las variaciones de los productos en el carrito del usuario actual
                    ex_var_list = [
                     list(item.variations.all()) for item in user_cart_items
                    ]
            
                    # Obtener los IDs de los elementos del carrito del usuario actual
                    user_cart_item_ids = list(user_cart_items.values_list("id", flat=True))

                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                    for cart_item in cart_items:
                        quantity = cart_item.quantity
                        

                    for pr in product_variation:
                        if pr in ex_var_list:
                            # Si una variación coincide, incrementar la cantidad
                            index = ex_var_list.index(pr)
                            item_id = user_cart_item_ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += quantity
                            item.user = user
                            item.save()
                        else:
                            # Si no hay coincidencias, agregar elementos al carrito del usuario
                            for item in cart_items:
                                item.user = user
                                item.save()
            except:
                pass
            # http://127.0.0.1:8000/accounts/login/?next=/cart/checkout/
            auth.login(request,user)
            messages.success(request,'Sesion exitosa')

            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                #next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                print(params)
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect ('dashboard')
            
        else:
            messages.error(request, 'las credenciales son incorrectas')
            return redirect('login')
    return render(request,'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Sesion Cerrada')
    
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Su cuenta se activo correctamente')
        return redirect('login')
    
    else:
        messages.error(request,'la activacion es invalida')
        return redirect ('register')
    
@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request,'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method =='POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Resetar Password'
            body = render_to_string('accounts/reset_password_email.html', {
            'user': user,
            'domain':current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user),
            })
            to_email=email
            send_email = EmailMessage(mail_subject,body,to=[to_email])
            send_email.send()

            messages.success(request,'Email enviado a tu bandeja de entrada para resetear contraseña')
            redirect('login')

        else:
            messages.error(request,'La cuenta de usuario no existe')
            return redirect('forgotPassword')
    return render (request,'accounts/forgotPassword.html')


def resetPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)


    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None  and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request, 'Por favor resetea tu password')
        return redirect ('resetPassword')
    else:
        messages.error(request,'El link ah expirado')
        return redirect('login')


def resetPassword(request):
    if request.method =='POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Se cambio correctamente el passoword')
            return redirect('login')
        else:
            messages.error(request,'Las contraseñas no coinciden')
            return redirect('resetPassword')

    else:
        return render(request,'accounts/resetPassword.html')
    
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders,
    }

    return render(request,'accounts/my_orders.html', context)


def edit_profile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)
    if request.method =='POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Su informacion fue guardada con exito')
            return redirect('edit_profile')
    else:
        
        user_form=UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
        print(user_form.errors)
        print(profile_form.errors)

    context ={
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }

    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']


        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()

                messages.success(request, 'El password se actualizo correctamnete')
                return redirect('change_password')
            else:
                messages.error(request,'Por favor ingrese una contraseña valida')
                return redirect('change_password')
            
        else:
            messages.error(request, 'El password con coincide')
            return redirect('change_password')
        
    return render(request, 'accounts/change_password.html')