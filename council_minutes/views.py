from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Request
from .docx import CouncilMinuteGenerator
from .helpers import QuerySetEncoder
import os
import json
from mongoengine.errors import ValidationError
from django.views.decorators.csrf import csrf_exempt #Esto va solo para evitar la verificacion de django


def index(request):
    return HttpResponse("¡Actas trabajando!")

@csrf_exempt #Esto va solo para evitar la verificacion de django
def filter_request(request):
    if request.method == 'GET':
        #Generic Query for Request model
        #To make a request check http://docs.mongoengine.org/guide/querying.html#query-operators
        params = json.loads(request.body)
        response = Request.objects.filter(**params).order_by('req_acad_prog')
        return JsonResponse(response, safe=False, encoder=QuerySetEncoder)
    
    else:
        return HttpResponse('Bad Request', status=400)


@csrf_exempt #Esto va solo para evitar la verificacion de django
def insert_request(request):
    if request.method == 'POST':
        new_request = Request().from_json(request.body)
        try:
            response = new_request.save()
            return HttpResponse(request.body, status=200)

        except ValidationError as e:
            return HttpResponse(e.message, status=400)

    else:
        return HttpResponse('Bad Request', status=400)

@csrf_exempt
def docx_gen_by_id(request):
    body = json.loads(request.body)
    filename = 'public/acta' + body["id"] + '.docx'
    request__by_id = Request.objects.get(id = body["id"])
    generator = CouncilMinuteGenerator()
    generator.add_case_from_request(request__by_id)
    generator.generate(filename)
    return HttpResponse(filename)