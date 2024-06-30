from django.http import JsonResponse
from django.shortcuts import render
from account.models import VisitorCount


def index(request):
    visitor_count, created = VisitorCount.objects.get_or_create(id=1)
    visitor_count.count += 1
    visitor_count.save()
    return render(request, 'index.html')