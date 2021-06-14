from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from django.shortcuts import get_object_or_404, get_list_or_404, render
from rest_framework.decorators import api_view, permission_classes, parser_classes

from quickstart.serializers import *
from quickstart.models import *

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['POST', 'GET', 'DELETE'])
@parser_classes([JSONParser])
@permission_classes([permissions.AllowAny])
def currentMedication(request, format=None):
    """
    Current medication taken by the user. 
    Args: 
        ...
    Return:
        [
            {
                String name,
                int dosageInMg,
                String consumption,
                String time,
                int totalDosage,
                int remainingDosage,
                bool prescription
            },
            {...},
            ...
        ]
    """
    if request.method == 'GET':
        patient_id = 1
        # 1. get all medication for a patient where dosage >= 0 and not redeemed
        medications_qs = get_list_or_404(
            Inventory, 
            userownsmedication__patient_id=patient_id,
            # still medication left, __gt = greater than 
            userownsmedication__remainingDosageInMg__gt=0, 
            # not yet redeemed
            userownsmedication__prescription_id__redeemed=False,
        )

        # 2. extract information from description
        # TODO: actual extraction, filter -- GPT3/sem search could be embedded here.
        how_to_consume = {
            "time":"twice a day"
        }

        # 3. create return package
        medications = []
        for medication in medications_qs: 
            # TODO: String consumption,
            medications.append(
                {
                    "name":medication.name, 
                    "medicationType":medication.medication_type_id.name,
                    "time":how_to_consume["time"],
                    "boughtTime":medication.userownsmedication_set.get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                    "dosageInMg":medication.ppDosageInMg,
                    "totalDosage":medication.totalDosageInMg,
                    "remainingDosage":medication.userownsmedication_set.get().remainingDosageInMg,
                    "prescription":medication.prescriptionNeeded,
                    "description":medication.description, 
                }
            )
        
        return Response(medications, status=status.HTTP_201_CREATED)

    elif request.method == 'POST': 
        patient_id = request.data["patient_id"]
        # 1. get all medication for a patient where dosage >= 0 and not redeemed
        medications_qs = get_list_or_404(
            Inventory, 
            userownsmedication__patient_id=patient_id,
            # still medication left, __gt = greater than 
            userownsmedication__remainingDosageInMg__gt=0, 
            # not yet redeemed
            userownsmedication__prescription_id__redeemed=False,
        )

        # 2. extract information from description
        # TODO: actual extraction, filter -- GPT3/sem search could be embedded here.
        how_to_consume = {
            "time":"twice a day"
        }

        # 3. create return package
        medications = []
        for medication in medications_qs: 
            # TODO: String consumption,
            medications.append(
                {
                    "name":medication.name, 
                    "medicationType":medication.medication_type_id.name,
                    "time":how_to_consume["time"],
                    "boughtTime":medication.userownsmedication_set.get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                    "dosageInMg":medication.ppDosageInMg,
                    "totalDosage":medication.totalDosageInMg,
                    "remainingDosage":medication.userownsmedication_set.get().remainingDosageInMg,
                    "prescription":medication.prescriptionNeeded,
                    "description":medication.description, 
                }
            )
        
        return Response(medications, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE': 
        pass
        return Response("DELETE", status=status.HTTP_200_OK)

    return Response("last error", status=status.HTTP_400_BAD_REQUEST)   

@api_view(['POST', 'GET', 'DELETE'])
@parser_classes([JSONParser])
@permission_classes([permissions.AllowAny])
def newPrescriptions(request, format=None):
    """
    Current medication taken by the user. 
    Args: 
        ...
    Return:
        [
            {
                String name,
                int dosageInMg,
                String consumption,
                String time,
                int totalDosage,
                int remainingDosage,
                bool prescription
            },
            {...},
            ...
        ]
    """
    if request.method == 'GET':
        # assessment_id = request.query_params.get("assessment_id", None)
        medications_qs = get_list_or_404(Product)
        medications = []
        for medication in medications_qs: 
            medications.append(
                {
                    "name":medication.name, 
                    "desc":medication.desc, 
                    "prescription":medication.prescription,
                }
            )
        return Response(medications, status=status.HTTP_200_OK)

    elif request.method == 'POST': 
        patient_id = request.data["patient_id"]
        # all medication for a patient where dosage >= 0
        medications_qs = get_list_or_404(
            Inventory, 
            userownsmedication__patient_id=patient_id,
            # __gt = greater than 
            userownsmedication__remainingDosageInMg__gt=0
        )
        medications = []
        for medication in medications_qs: 
            medications.append(
                {
                    "name":medication.name, 
                    "time":medication.userownsmedication_set.get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                    "dosageInMg":medication.ppDosageInMg,
                    "totalDosage":medication.totalDosageInMg,
                    "remainingDosage":medication.userownsmedication_set.get().remainingDosageInMg,
                    "prescription":medication.prescriptionNeeded,
                    "description":medication.desc, 
                }
            )
        
        return Response(medications, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE': 
        pass
        return Response("DELETE", status=status.HTTP_200_OK)

    return Response("last error", status=status.HTTP_400_BAD_REQUEST)   