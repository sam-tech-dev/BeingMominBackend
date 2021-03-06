"""
This view is used for login the user and generate the json file for
that user which user is belong in survey app.
"""
import ast
import json
import logging
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from AmbassadorPortal.models import people
from portal_utils import get_person_from_id
from django.db.models import Q

logger = logging.getLogger('django')


@api_view(['POST'])
@permission_classes((AllowAny,))
def view_search_person(request):
    """
    This view is used for login and generates json for user access.
    :param request: contain username and password of user.
    :return: json for generate UI dynamically.
    """
    response = {}
    body = None
    try:
        body_unicode = request.body.decode('utf-8')
        body = ast.literal_eval(body_unicode)
        search_name = body['searchName']
        locality = body['locality']
        gender = body['gender']

        print("gender : "+gender)
        print("locality : "+locality)

        response["Status"] = 0

        con1= Q(name__icontains=search_name)
        con2 = Q(gender=gender)
        con3 = Q(locality_id__locality_key= locality)

        if(locality.__len__()!=0 & gender.__len__()!=0 ):
          persons_array = people.objects.filter(con1 & con2
                                                & con3).values('id','name','locality__locality_key','father_id')
        elif (locality.__len__() == 0 & gender.__len__() != 0):
          persons_array = people.objects.filter(name__icontains=search_name, gender=gender).values('id', 'name','locality__locality_key','father_id')

        elif (locality.__len__() != 0 & gender.__len__() == 0):
            persons_array = people.objects.filter(name__icontains=search_name, locality_id__locality_key=locality).values('id', 'name', 'locality__locality_key','father_id')

        elif (locality.__len__() == 0 & gender.__len__() == 0):
            persons_array = people.objects.filter(name__icontains=search_name).values('id', 'name', 'locality__locality_key','father_id')

        persons = []
        persons_list = list(persons_array)

        for person in persons_list:

            if person["father_id"]==0:
              father_name=""
            else:
              father_name= get_person_from_id(person["father_id"]).name
            personDict = {
                "id":person["id"],
                "name": person["name"],
                "locality" : person["locality__locality_key"],
                "father": father_name
            }
            persons.append(personDict)

        response["persons"]=persons

    except Exception as e:
        response = {"Status": 1}
        logger.error("Body of Request is'{0}' and Exception is '{1}'".format(body, e), exc_info=True)

    return HttpResponse(json.dumps(response), content_type='application/json')
