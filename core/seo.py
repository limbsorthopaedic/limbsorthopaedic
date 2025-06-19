
from django.conf import settings
from django.urls import reverse
import json

class SEOManager:
    """Centralized SEO management for LIMBS Orthopaedic"""
    
    # Primary keywords and products
    PRIMARY_KEYWORDS = [
        'orthopaedic', 'prosthetics', 'orthotic devices', 'AFO', 'KAFO', 'HKAFO',
        'transfemoral prosthesis', 'transtibial prosthesis', 'wheelchair', 'crutches',
        'spinal brace', 'splints', 'arch support', 'orthotics Nairobi', 'prosthetics Kenya'
    ]
    
    PRODUCTS = [
        'Aeroplane splint', 'AFO (Adult)', 'AFO (Child)', 'Arch support (Child)',
        'Arch support (Rigid, Adult)', 'Arch support (Soft, Adult)', 'Axillary crutch',
        'Calcaneal spur insole', 'Cockup splint (Adult)', 'Cockup splint (Child)',
        'Derotator Harness', 'Elbow conformer (Adult)', 'Elbow conformer (Child)',
        'Elbow crutch', 'Genu Varus and Genu Valgum splints', 'Hand resting splint (Adult)',
        'Hand resting splint (Child)', 'HKAFO (Adult)', 'HKAFO (Child)', 'HTHKAFO',
        'KAFO', 'Lateral and Medial wedges (Adult)', 'Lateral and Medial wedges (Child)',
        'Neck collar (Adult)', 'Neck collar (Child)', 'Prosthetic Socket replacement',
        'Raising (per 1cm)', 'SMAFO', 'Spinal Brace (Adult)', 'Spinal Brace (Child)',
        'Standard Wheelchair', 'Standing And Sitting AID', 'THKAFO',
        'Transfemoral prosthesis', 'Transtibial Prosthesis', 'Walking frame', 'GRAFO'
    ]
    
    SERVICES = [
        'Prosthetic fitting', 'Orthotic fabrication', 'Gait training', 'Physiotherapy',
        'Orthopaedic consultation', 'Mobility assessment', 'Device repair',
        'Custom orthotics', 'Prosthetic maintenance', 'Rehabilitation therapy'
    ]
    
    @staticmethod
    def get_meta_keywords():
        """Generate meta keywords for the site"""
        return ', '.join(SEOManager.PRIMARY_KEYWORDS + SEOManager.PRODUCTS[:15])
    
    @staticmethod
    def get_product_keywords():
        """Get product-specific keywords"""
        return ', '.join(SEOManager.PRODUCTS)
    
    @staticmethod
    def get_service_keywords():
        """Get service-specific keywords"""
        return ', '.join(SEOManager.SERVICES)
    
    @staticmethod
    def generate_structured_data(request, page_type='website', **kwargs):
        """Generate JSON-LD structured data"""
        base_url = f"https://{request.get_host()}"
        
        # Base organization schema
        organization = {
            "@context": "https://schema.org",
            "@type": "MedicalBusiness",
            "name": "LIMBS Orthopaedic",
            "description": "Premier orthopaedic clinic in Nairobi, Kenya specializing in prosthetics, orthotic devices, and mobility aids",
            "url": base_url,
            "logo": "https://i.imgur.com/V6XTdBi.jpg",
            "image": "https://i.imgur.com/V6XTdBi.jpg",
            "telephone": ["+254719628276", "+254714663594", "+254705347657"],
            "email": "LimbsOrthopaedic@gmail.com",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Kasarani",
                "addressLocality": "Nairobi",
                "addressCountry": "Kenya"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "-1.2921",
                "longitude": "36.8219"
            },
            "openingHours": "Mo-Sa 08:00-18:00",
            "medicalSpecialty": [
                "Orthopaedics",
                "Prosthetics",
                "Orthotics",
                "Rehabilitation Medicine"
            ],
            "priceRange": "$$",
            "paymentAccepted": ["Cash", "Mobile Money", "Bank Transfer"],
            "currenciesAccepted": "KES"
        }
        
        if page_type == 'product':
            product_data = {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": kwargs.get('name', ''),
                "description": kwargs.get('description', ''),
                "brand": {
                    "@type": "Brand",
                    "name": "LIMBS Orthopaedic"
                },
                "manufacturer": organization,
                "category": "Medical Device",
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "priceCurrency": "KES",
                    "price": kwargs.get('price', 'Price on Request')
                }
            }
            return [organization, product_data]
        
        elif page_type == 'service':
            service_data = {
                "@context": "https://schema.org",
                "@type": "MedicalProcedure",
                "name": kwargs.get('name', ''),
                "description": kwargs.get('description', ''),
                "performer": organization,
                "medicalSpecialty": "Orthopaedics"
            }
            return [organization, service_data]
        
        return [organization]
    
    @staticmethod
    def get_breadcrumb_schema(request, breadcrumbs):
        """Generate breadcrumb structured data"""
        base_url = f"https://{request.get_host()}"
        items = []
        
        for i, (name, url) in enumerate(breadcrumbs, 1):
            items.append({
                "@type": "ListItem",
                "position": i,
                "name": name,
                "item": f"{base_url}{url}" if url else base_url
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
