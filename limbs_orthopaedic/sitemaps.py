from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'about', 'services', 'products', 'contact', 'gallery:gallery', 'testimonials', 'blog']

    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
