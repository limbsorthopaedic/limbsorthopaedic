from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import BlogPost, BlogCategory, Comment
from core.models import SocialMedia


class BlogListView(ListView):
    """View for displaying all blog posts or posts by category"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published')
        category_slug = self.kwargs.get('category_slug')
        
        if category_slug:
            category = get_object_or_404(BlogCategory, slug=category_slug, is_active=True)
            queryset = queryset.filter(categories=category)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        context['current_category'] = self.kwargs.get('category_slug')
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context


class BlogDetailView(DetailView):
    """View for displaying a single blog post"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Get approved comments for this post
        context['comments'] = post.comments.filter(is_approved=True)
        
        # Get related posts based on categories
        post_categories = post.categories.all()
        related_posts = BlogPost.objects.filter(
            status='published',
            categories__in=post_categories
        ).exclude(id=post.id).distinct()[:3]
        context['related_posts'] = related_posts
        
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        context['social_media'] = SocialMedia.objects.filter(is_active=True)
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comment submission"""
        post = self.get_object()
        
        # Create a new comment
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')
        
        if name and email and content:
            Comment.objects.create(
                post=post,
                name=name,
                email=email,
                content=content
            )
            messages.success(request, 'Your comment has been submitted and is awaiting approval.')
        else:
            messages.error(request, 'Please fill in all the required fields.')
        
        return HttpResponseRedirect(reverse('blog_detail', kwargs={'slug': post.slug}))
