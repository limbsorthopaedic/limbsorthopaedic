from django.shortcuts import render

def handler404(request, exception):
    """
    Custom 404 page not found handler
    """
    return render(request, 'errors/404.html', status=404)

def handler403(request, exception):
    """
    Custom 403 permission denied handler
    """
    return render(request, 'errors/403.html', status=403)

def handler500(request):
    """
    Custom 500 server error handler
    """
    return render(request, 'errors/500.html', status=500)