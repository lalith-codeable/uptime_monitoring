from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

def error_404_view(request, exception):
    return render(request, '404.html')