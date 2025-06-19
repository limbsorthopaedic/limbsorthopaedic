from django.urls import path
from .views import (
    ProductListView, ProductDetailView, add_to_cart, cart_view,
    update_cart_item, remove_from_cart, checkout_view, place_order,
    order_confirmation, get_cart_count
)

urlpatterns = [
    path('', ProductListView.as_view(), name='products'),
    path('category/<slug:category_slug>/', ProductListView.as_view(), name='products_by_category'),
    path('cart/', cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/count/', get_cart_count, name='get_cart_count'),
    path('checkout/', checkout_view, name='checkout_view'),
    path('place-order/', place_order, name='place_order'),
    path('order/<str:order_number>/', order_confirmation, name='order_confirmation'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]
