from django.shortcuts import render

def home(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, "home.html", context)