
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.models import User
from services.models import Service
from products.models import Product
from blog.models import BlogPost
from .models import ChatMessage
import json
import re
import uuid

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '').lower()
        conversation_id = data.get('conversation_id')
        
        # Get the hostname from the request
        host = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        base_url = f"{protocol}://{host}"
        
        # Check if we are starting a new conversation
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Search for relevant content
        services = Service.objects.filter(
            Q(title__icontains=user_message) | 
            Q(description__icontains=user_message)
        )
        products = Product.objects.filter(
            Q(title__icontains=user_message) | 
            Q(description__icontains=user_message)
        )
        blog_posts = BlogPost.objects.filter(
            Q(title__icontains=user_message) | 
            Q(content__icontains=user_message)
        )
        
        # Keywords for specific responses
        appointment_keywords = ['appointment', 'book', 'schedule', 'visit', 'meet', 'doctor', 'consultation']
        location_keywords = ['location', 'address', 'where', 'find', 'directions', 'located', 'office', 'clinic', 'hospital']
        contact_keywords = ['contact', 'phone', 'call', 'email', 'whatsapp', 'reach', 'number']
        price_keywords = ['price', 'cost', 'fee', 'payment', 'pay', 'insurance', 'nhif', 'bill', 'affordable']
        hours_keywords = ['hours', 'open', 'close', 'time', 'operating', 'available', 'working', 'schedule']
        history_keywords = ['history', 'transcript', 'previous', 'conversation', 'export', 'save', 'record', 'download']
        product_keywords = ['product', 'products', 'device', 'devices', 'equipment', 'crutches', 'wheelchair', 'walker', 'mobility', 'aid', 'aids', 'standing', 'sitting']
        service_keywords = ['service', 'services', 'treatment', 'treatments', 'help', 'prosthetic', 'orthotic', 'rehabilitation', 'therapy', 'medical', 'care', 'orthopaedic', 'physiotherapy', 'consultation']
        
        # Handle history/export requests
        if any(keyword in user_message for keyword in history_keywords):
            response = "📋 *Chat History & Export*\n\n"
            response += "Your conversation is automatically saved to our system.\n\n"
            response += "To access or export your chat history:\n"
            response += "1. If you're logged in, visit your account page\n"
            response += "2. For a copy of this conversation, use the 'Export Chat' button below\n\n"
            response += "Your conversation ID is: " + conversation_id
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id,
                'allow_export': True
            })
        
        # Handle greetings
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', 'hola', 'hi there']
        if any(greeting == user_message.lower() or greeting == user_message.lower().strip() for greeting in greetings):
            response = "👋 Hello! I'm the LIMBS Orthopaedic virtual assistant. How can I help you today?\n\nYou can ask me about:\n• Our services\n• Our products (mobility aids)\n• Book an appointment\n• Location and directions\n• Contact information\n• Operating hours\n• Exporting chat history"
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id
            })
            
        # Handle appointment inquiries
        if any(keyword in user_message for keyword in appointment_keywords):
            response = "📅 *Booking an Appointment*\n\n"
            response += "You can easily book an appointment with our specialists through our online booking system.\n\n"
            response += f"👉 Book online: {base_url}/appointments/\n\n"
            response += "Or contact us directly:\n"
            response += "📞 Call Collins: +254719628276\n"
            response += "📞 Call Kelvine: +254714663594\n"
            response += "📱 WhatsApp Collins: https://wa.me/254719628276\n\n"
            response += "📱 WhatsApp Kelvine: https://wa.me/254719628276\n\n"
            response += "Please let us know if you have any specific requirements or questions about your appointment."
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id
            })
            
        # Handle location inquiries
        if any(keyword in user_message for keyword in location_keywords):
            response = "📍 Our Location\n\n"
            response += "LIMBS Orthopaedic is located in ICIPE Road, Kasarani, Nairobi, Kenya.\n\n"
            response += "🧭 Get directions: https://maps.app.goo.gl/nGq6tDea9xBby4m49\n\n"
            response += "If you need help with directions, please feel free to contact us at:\n\n"
            response += "📞 Call Collins: +254719628276\n"
            response += "📞 Call Kelvine: +254714663594\n\n"
            response += "📱 WhatsApp Collins: https://wa.me/254719628276\n"
            response += "📱 WhatsApp Kelvine: https://wa.me/254719628276\n\n"
            response += "Thank you."
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id
            })
            
        # Handle contact inquiries
        if any(keyword in user_message for keyword in contact_keywords):
            response = "☎️ *Contact Information*\n\n"
            response += "We're always here to help! Here's how you can reach us:\n\n"
            response += "📞 Phone: +254719628276 (Collins), +254714663594 (Kelvine), or +254705347657 (Office)\n\n"
            response += "📱 WhatsApp Collins: https://wa.me/254719628276\n"
            response += "📱 WhatsApp Kelvine: https://wa.me/254714663594\n\n"
            response += "📧 Email: LimbsOrthopaedic@gmail.com\n\n"
            response += f"🔗 Website: {base_url}\n\n"
            response += "Our team is available during business hours to assist you with any questions or concerns."
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id
            })

        # Handle price inquiries
        if any(keyword in user_message for keyword in price_keywords):
            response = "💰 *Pricing Information*\n\n"
            response += "Our prices vary depending on the specific service and your individual needs.\n\n"
            response += "We offer:\n"
            response += "• Competitive pricing for all orthopaedic services\n"
            response += "• NHIF coverage for eligible treatments\n"
            response += "• Payment plans for certain procedures\n\n"
            response += "For a personalized quote, please:\n"
            response += "📞 Call Collins: +254719628276\n"
            response += "📞 Call Kelvine: +254714663594\n\n"
            response += "📱 WhatsApp Collins: https://wa.me/254719628276\n"
            response += "📱 WhatsApp Kelvine: https://wa.me/254714663594\n\n"
            response += f"🔗 Book a consultation: {base_url}/appointments/\n\n"
            response += "We're committed to providing accessible care to all our patients."
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id
            })

        # Handle hours inquiries
        if any(keyword in user_message for keyword in hours_keywords):
            response = "⏰ *Operating Hours*\n\n"
            response += "Our clinic is open as follows:\n\n"
            response += "Monday - Friday: 8:00 AM - 5:00 PM\n"
            response += "Saturday: 9:00 AM - 12:00 NOON\n"
            response += "Sunday: Closed\n\n"
            response += "For emergencies outside regular hours, please call Collins: +254719628276 or Call Kelvine: +254714663594."
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id
            })
            
        # Handle service inquiries
        if any(keyword in user_message for keyword in service_keywords):
            # Fetch active services
            active_services = Service.objects.filter(is_active=True).order_by('order', 'title')
            
            response = "🏥 *Our Medical Services*\n\n"
            response += "We offer comprehensive orthopaedic and rehabilitation services:\n\n"
            
            # List all active services with links
            for service in active_services:
                service_url = f"{base_url}/services/{service.slug}/"
                response += f"• *{service.title}*\n"
                response += f"  👉 {service_url}\n\n"
            
            response += "Need personalized care? Our specialists are here to help!\n\n"
            response += "📞 Call: Collins: +254719628276 or Kelvine: +254714663594\n\n"
            response += "📱 WhatsApp: Collins: https://wa.me/254719628276 or Kelvine: https://wa.me/254714663594\n"
            response += f"📅 Book an appointment: {base_url}/appointments/"
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id
            })
            
        # Handle product inquiries
        if any(keyword in user_message for keyword in product_keywords):
            # Fetch active products
            active_products = Product.objects.filter(is_active=True)
            
            response = "🦽 *Our Mobility Products*\n\n"
            response += "We offer a range of high-quality mobility aids and devices to improve your quality of life:\n\n"
            
            # List all active products with links
            for product in active_products:
                product_url = f"{base_url}/products/{product.slug}/"
                response += f"• *{product.title}*\n"
                response += f"  👉 {product_url}\n\n"
            
            response += "Can't find what you're looking for? We offer custom product solutions!\n"
            response += f"🔗 Request a custom product: {base_url}/products/#custom-request\n\n"
            response += "For ordering or inquiries:\n"
            response += "📞 Call: +254719628276\n"
            response += "📞 Call: +254714663594\n\n"
            response += "📱 WhatsApp: https://wa.me/254719628276\n"
            response += "📱 WhatsApp: https://wa.me/254714663594"
            
            # Save the message exchange
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key if not user else None
            
            chat_message = ChatMessage(
                user_message=user_message,
                ai_response=response,
                conversation_id=conversation_id,
                user=user,
                session_key=session_key
            )
            chat_message.save()
            
            return JsonResponse({
                'answer': response,
                'conversation_id': conversation_id
            })

        # Construct response for content matches
        if services.exists():
            service = services.first()
            service_url = f"{base_url}/services/{service.slug}/"
            
            response = f"*{service.title}*\n\n"
            # Clean description by removing HTML tags
            clean_description = re.sub(r'<[^>]*>', '', service.description)
            response += f"{clean_description[:200]}...\n\n"
            
            response += "Would you like to:\n\n"
            response += f"👉 Learn more: {service_url}\n"
            response += f"📅 Book an appointment: {base_url}/appointments/\n"
            response += "☎️ Contact us:\n"
            response += "📞 Call: Collins: +254719628276 or Kelvine: +254714663594\n\n"
            response += "📱 WhatsApp: Collins: https://wa.me/254719628276 or Kelvine: https://wa.me/254714663594"
            
        elif products.exists():
            product = products.first()
            product_url = f"{base_url}/products/{product.slug}/"
            
            response = f"*{product.title}*\n\n"
            # Clean description by removing HTML tags
            clean_description = re.sub(r'<[^>]*>', '', product.description)
            response += f"{clean_description[:200]}...\n\n"
            
            if product.price:
                response += f"💰 Price: KSh {product.price}\n\n"
                
            response += f"👉 View details: {product_url}\n"
            response += "📱 Order via WhatsApp: Collins: https://wa.me/254719628276 or Kelvine: https://wa.me/254714663594"
            
        elif blog_posts.exists():
            post = blog_posts.first()
            post_url = f"{base_url}/blog/{post.slug}/"
            
            response = f"*{post.title}*\n\n"
            # Clean content by removing HTML tags
            clean_content = re.sub(r'<[^>]*>', '', post.content)
            response += f"{clean_content[:200]}...\n\n"
            
            response += f"👉 Read the full article: {post_url}\n\n"
            response += "For more information about our services, feel free to:\n"
            response += f"📅 Book a consultation: {base_url}/appointments/\n"
            response += "📞 Call us: Collins: +254719628276 or Kelvine: +254714663594"
            
        else:
            # Generic response for unmatched queries
            response = "I'm here to help! I can provide information about:\n\n"
            response += "🏥 Our medical services and treatments\n"
            response += "🦽 Mobility products and devices\n"
            response += "📅 Appointment booking\n"
            response += "📍 Location and directions\n"
            response += "☎️ Contact information\n"
            response += "⏰ Operating hours\n"
            response += "💰 Pricing and payment options\n\n"
            response += "What would you like to know more about?"
        
        # Save the message exchange
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key if not user else None
        
        chat_message = ChatMessage(
            user_message=user_message,
            ai_response=response,
            conversation_id=conversation_id,
            user=user,
            session_key=session_key
        )
        chat_message.save()
        
        return JsonResponse({
            'answer': response,
            'conversation_id': conversation_id
        })
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def export_chat(request):
    """Export chat history as text file"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            conversation_id = data.get('conversation_id')
            
            if not conversation_id:
                return JsonResponse({'error': 'Conversation ID is required'}, status=400)
                
            # Fetch conversation messages
            messages = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('created_at')
            
            if not messages.exists():
                return JsonResponse({'error': 'No messages found for this conversation'}, status=404)
                
            # Build conversation text
            from django.utils import timezone
            
            conversation_text = f"Chat Conversation ID: {conversation_id}\n"
            conversation_text += f"Exported on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for msg in messages:
                conversation_text += f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}]\n"
                conversation_text += f"User: {msg.user_message}\n"
                conversation_text += f"AI: {msg.ai_response}\n\n"
                
            # Return as text response for download
            return JsonResponse({
                'success': True,
                'content': conversation_text,
                'filename': f"chat_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.txt"
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)
