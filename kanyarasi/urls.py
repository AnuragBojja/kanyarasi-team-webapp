"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('user_register/', views.user_register, name='user_register'),
    path('user_login/', include([
        path('', views.user_login, name='user_login'),
        path('user_dash/', views.user_dash, name='user_dash'),
        path('order_status/', views.order_status, name='order_status'),
        path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
        path('user_dash/', include([
            path('', views.user_dash, name='user_dash'),
            path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
            path('cart/', views.cart_view, name='cart_view'),
            path('cart/remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
            path('user_dash/cart/get_cart_items/', views.get_cart_items, name='get_cart_items'),
            path('cart/', include([
                path('', views.get_cart_items, name='cart'),
                path('get_cart_items/', views.get_cart_items, name='get_cart_items'),
            ])),
            path('submit_order/', views.submit_order, name='submit_order'),
        ])),
    ])),

    path('master_register/', views.master_register, name='master_register'),
    path('master_login/', views.master_login, name='master_login'),
    path('master_login/', include([
        path('', views.master_login, name='master_login'),
        path('master_dash/', views.master_dash, name='master_dash'),
        path('master_dash/', include([
            path('', views.master_dash, name='master_dash'),
            path('add_item/', views.add_item, name='add_item'),
            path('view_menu/', views.view_menu, name='view_menu'),
            path('view_order/', views.view_order, name='view_order'),
            path('view_order/', include([
                path('', views.view_order, name='view_order'),
                path('complete_order_page/<int:order_id>/', views.complete_order_page, name='complete_order_page'),
                path('confirm_complete_order/<int:order_id>/', views.confirm_complete_order, name='confirm_complete_order'),

            ])),
        ])),
    ])),

    path('captain_register/', views.captain_register, name='captain_register'),
    path('captain_login/', views.captain_login, name='captain_login'),
    path('captain_login/', include([
        path('', views.captain_login, name='captain_login'),
        path('cap_dash/', views.cap_dash, name='cap_dash'),
        path('cancel_order/', views.cancel_order, name='cancel_order'),
        #path('deliver_order/<int:order_id>/', views.deliver_order, name='deliver_order'),
        path('cap_dash/', include([
            path('', views.cap_dash, name='cap_dash'),
            path('deliver_order/<int:order_id>/', views.deliver_order, name='deliver_order'),

        ])),
    ])),
    path('mark_order_delivered/<int:order_id>/', views.mark_order_delivered, name='mark_order_delivered'),
    path('order_status/', views.order_status, name='order_status'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)