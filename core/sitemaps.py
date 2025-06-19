
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'services', 'products', 'contact', 'gallery:gallery', 'testimonials', 'blog']

    def location(self, item):
        return reverse(item)
        
    def lastmod(self, item):
        return None
