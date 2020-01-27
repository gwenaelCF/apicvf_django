from django.shortcuts import render
from django.http import HttpResponse

import cdp.models
# Create your views here.

def index(request):
	if request.method == 'POST':
		dp = cdp.models.CdpApic(request.files['file'])
		return HttpResponse(f"{dp.name} reçu à {dp.dt} avec {dt.grains}")	

    return HttpResponse("Hello World from django app CDP (I want a post, please gimme a post)")
