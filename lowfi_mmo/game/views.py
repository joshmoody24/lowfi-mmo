from django.shortcuts import render

def index(request):
    return render(request, "index.html")

def example(request):
    return render(request, "pico_example.html")