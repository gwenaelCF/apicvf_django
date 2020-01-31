from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import InMemoryUploadedFile

import cdp.models
# Create your views here.

@csrf_exempt
def index(request):
    if request.method == 'POST':
        #dp = cdp.models.CdpApic.create(request.FILES['file'])
        dp = request.FILES['file']
        response_content = dp.name
        return HttpResponse(
            response_content
            )
    else :
        response = HttpResponse()
        response.status_code = 405
        response.write("method POST required")
        return response