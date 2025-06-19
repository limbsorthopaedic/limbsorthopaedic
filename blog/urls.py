from django.urls import path
from .views import BlogListView, BlogDetailView

urlpatterns = [
    path('', BlogListView.as_view(), name='blog'),
    path('category/<slug:category_slug>/', BlogListView.as_view(), name='blog_by_category'),
    path('<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
]
