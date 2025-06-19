from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import Product, ProductCategory, CustomProductRequest, Cart, CartItem, Order, OrderItem
from .forms import CustomProductRequestForm
from core.models import SocialMedia
from core.seo import SEOManager


class ProductListView(ListView):
    """View for displaying all products or products by category"""
    model = Product
    template_name = 'products/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            category = get_object_or_404(ProductCategory, slug=category_slug, is_active=True)
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['current_category'] = self.kwargs.get('category_slug')
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        context['custom_product_form'] = CustomProductRequestForm()

        # SEO data
        context['meta_keywords'] = SEOManager.get_product_keywords()
        context['structured_data'] = SEOManager.generate_structured_data(self.request)
        context['breadcrumbs'] = [('Home', '/'), ('Products', '/products/')]
        context['breadcrumb_schema'] = SEOManager.get_breadcrumb_schema(self.request, context['breadcrumbs'])
        return context

    def post(self, request, *args, **kwargs):
        form = CustomProductRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your custom product request has been submitted. We'll contact you soon to discuss your needs.")
            return redirect('products')
        else:
            # Re-render the page with the form errors
            context = self.get_context_data(**kwargs)
            context['custom_product_form'] = form
            return render(request, self.template_name, context)


class ProductDetailView(DetailView):
    """View for displaying a single product"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related products in the same category
        product = self.get_object()
        context['related_products'] = Product.objects.filter(
            category=product.category, 
            is_active=True
        ).exclude(id=product.id)[:4]
        context['social_media'] = SocialMedia.objects.filter(is_active=True)

        # SEO data
        context['meta_keywords'] = f"{product.title}, {product.category.name}, orthopaedic products Kenya, prosthetics Nairobi"
        context['structured_data'] = SEOManager.generate_structured_data(
            self.request, 
            page_type='product',
            name=product.title,
            description=product.description,
            price=product.formatted_price
        )
        context['breadcrumbs'] = [
            ('Home', '/'), 
            ('Products', '/products/'), 
            (product.title, f'/products/{product.slug}/')
        ]
        context['breadcrumb_schema'] = SEOManager.get_breadcrumb_schema(self.request, context['breadcrumbs'])
        return context


def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


@require_POST
def add_to_cart(request, product_id):
    """Add product to cart"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)
        quantity = int(request.POST.get('quantity', 1))
        notes = request.POST.get('notes', '')
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'notes': notes}
        )
        
        if not created:
            cart_item.quantity += quantity
            if notes:
                cart_item.notes = notes
            cart_item.save()
        
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'{product.title} added to cart',
                'cart_total': cart.total_items
            })
        else:
            messages.success(request, f'{product.title} has been added to your cart.')
            return redirect('cart_view')
            
    except ValueError as e:
        error_msg = 'Invalid quantity specified.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        else:
            messages.error(request, error_msg)
            return redirect('product_detail', slug=product.slug)
    except Exception as e:
        error_msg = 'Error adding product to cart. Please try again.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        else:
            messages.error(request, error_msg)
            return redirect('product_detail', slug=product.slug)


def cart_view(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    cart_items = cart.get_items()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'social_media': SocialMedia.objects.filter(is_active=True),
        'breadcrumbs': [('Home', '/'), ('Cart', '/cart/')],
    }
    context['breadcrumb_schema'] = SEOManager.get_breadcrumb_schema(request, context['breadcrumbs'])
    
    return render(request, 'products/cart.html', context)


@require_POST
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total': cart.total_items,
                'item_total': cart_item.get_total_price() if quantity > 0 else 0,
                'cart_subtotal': cart.total_price
            })
        else:
            messages.success(request, 'Cart updated successfully.')
            return redirect('cart_view')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': str(e)})
        else:
            messages.error(request, 'Error updating cart.')
            return redirect('cart_view')


@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_title = cart_item.product.title
        cart_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product_title} removed from cart',
                'cart_total': cart.total_items
            })
        else:
            messages.success(request, f'{product_title} has been removed from your cart.')
            return redirect('cart_view')
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': str(e)})
        else:
            messages.error(request, 'Error removing item from cart.')
            return redirect('cart_view')


def checkout_view(request):
    """Checkout page"""
    cart = get_or_create_cart(request)
    cart_items = cart.get_items()
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart_view')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'social_media': SocialMedia.objects.filter(is_active=True),
        'breadcrumbs': [('Home', '/'), ('Cart', '/cart/'), ('Checkout', '/checkout/')],
    }
    context['breadcrumb_schema'] = SEOManager.get_breadcrumb_schema(request, context['breadcrumbs'])
    
    return render(request, 'products/checkout.html', context)


@require_POST
@transaction.atomic
def place_order(request):
    """Place an order"""
    try:
        cart = get_or_create_cart(request)
        cart_items = cart.get_items()
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart_view')
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=request.POST.get('customer_name'),
            customer_email=request.POST.get('customer_email'),
            customer_phone=request.POST.get('customer_phone'),
            shipping_address=request.POST.get('shipping_address'),
            shipping_city=request.POST.get('shipping_city'),
            shipping_notes=request.POST.get('shipping_notes', ''),
            notes=request.POST.get('notes', ''),
            total_amount=cart.total_price,
            status='pending'
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price or 0,
                notes=cart_item.notes or ''
            )
        
        # Send order confirmation email
        order.send_status_email()
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, f'Your order #{order.order_number} has been placed successfully. We will contact you shortly.')
        return redirect('order_confirmation', order_number=order.order_number)
        
    except Exception as e:
        messages.error(request, f'Error placing order: {str(e)}')
        return redirect('checkout_view')


def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
        'social_media': SocialMedia.objects.filter(is_active=True),
        'breadcrumbs': [('Home', '/'), ('Order Confirmation', f'/order/{order_number}/')],
    }
    context['breadcrumb_schema'] = SEOManager.get_breadcrumb_schema(request, context['breadcrumbs'])
    
    return render(request, 'products/order_success.html', context)


def get_cart_count(request):
    """AJAX endpoint to get cart item count"""
    cart = get_or_create_cart(request)
    return JsonResponse({'count': cart.total_items})