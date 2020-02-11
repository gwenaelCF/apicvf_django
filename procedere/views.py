from django.shortcuts import render
from django.http import HttpResponse


def index(request):
	resp = f"Hello, world. You're at the procedere index."
	return HttpResponse(resp)
