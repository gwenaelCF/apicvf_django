from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import InMemoryUploadedFile

from . import reception_cdp
from mflog import get_logger
#import cdp.models
# Create your views here.


def index(request):
    resp = f"Hello, world. You're at the procedere index."
    return HttpResponse(resp)


@csrf_exempt
def cdp(request):
    if request.method == 'POST':
        logger = get_logger("requete_cdp")
        logger.debug("avant thread")
        dp = request.FILES['file']
        # lancement des traitements
        reception_cdp.reception_cdp(dp)
        logger.debug("après lancement thread")
        response_content = dp.name
        return HttpResponse(
            response_content
        )
    else:
        response = HttpResponse()
        response.status_code = 405
        response.write("method POST required")
        return response
