
from django.views.generic import ListView
from .models import Gallery
from core.models import SocialMedia

class GalleryListView(ListView):
    model = Gallery
    template_name = 'gallery/gallery.html'
    context_object_name = 'galleries'
    queryset = Gallery.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context
