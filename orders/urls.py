from django.urls import path , include
from .import views

urlpatterns=[
    path('place_order/', views.place_order, name='place_order'),
    path('paypal/',include('paypal.standard.ipn.urls')),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    #path('ipn_handler/', views.ipn_handler, name='ipn_hadler'), 
    path('pruebas/<int:order_number>/', views.pruebas, name='pruebas')
    #path('payment-success/<int:product_id>/', views.PaymentSuccessful, name='payment-success'),
    #path('payment-failed/<int:product_id>/', views.paymentFailed, name='payment-failed'),
]
