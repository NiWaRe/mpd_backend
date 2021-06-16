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
    Current medication taken by the patient.
    GET, DELETE not implemented for now. 
    Args: 
        patient_id, int
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
        # some_get_param = request.query_params.get("some_get_param", None)
        return Response(
            "Not implemented, please specify a patient_id (POST call)", 
            status=status.HTTP_204_NO_CONTENT
        )

    elif request.method == 'POST': 
        patient_id = request.data["patient_id"]
        # 1. get all medication for a patient where dosage >= 0 and already redeemed
        medications_qs = get_list_or_404(
            Inventory, 
            patientownsmedication__patient_id=patient_id,
            # still medication left, __gt = greater than 
            patientownsmedication__remainingDosageInMg__gt=0, 
            # already redeemed
            patientownsmedication__prescription_id__redeemed=True,
        )

        # 2. extract information from description
        # TODO: actual extraction, filter -- GPT3/sem search could be embedded here.
        how_to_consume = {
            "time":"twice a day"
        }

        # 3. create return package
        medications = []
        for medication in medications_qs: 
            medications.append(
                {
                    "medication_name":medication.name, 
                    "medication_id":medication.medication_id,
                    "medicationType":medication.medication_type_id.name,
                    "time":how_to_consume["time"],
                    "totalPriceInEur":medication.totalPriceInEUR,
                    "boughtTime":medication.patientownsmedication_set.get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                    "dosageInMg":medication.ppDosageInMg,
                    "totalDosage":medication.totalDosageInMg,
                    "remainingDosage":medication.patientownsmedication_set.get().remainingDosageInMg,
                    "prescription":medication.prescriptionNeeded,
                    "description":medication.description, 
                }
            )
        
        return Response(medications, status=status.HTTP_200_OK)

    elif request.method == 'DELETE': 
        return Response("Not implemented yet", status=status.HTTP_204_NO_CONTENT)

    # something went wrong - none of the above cases was called
    return Response("last error", status=status.HTTP_400_BAD_REQUEST)   

@api_view(['POST', 'GET', 'DELETE'])
@parser_classes([JSONParser])
@permission_classes([permissions.AllowAny])
def newPrescriptions(request, format=None):
    """
    Current medication from unredeemed prescriptions. 
    GET, DELETE not implemented for now. 
    Args: 
        patient_id, int
    Return:
        [
            {
                String prescription_name;
                Int prescription_id;
                String doctor_name;
                ...
                DateTime date;
                medications: [
                    {
                        <MedicationInformation>
                    }, 
                    {...},
                    ...
                ]
            },
            {...},
            ...
        ]
    """
    if request.method == 'GET':
        return Response(
            "Not implemented, please specify a patient_id (POST call)", 
            status=status.HTTP_204_NO_CONTENT
        )

    elif request.method == 'POST': 
        patient_id = request.data["patient_id"]
        # 1. get all medication from all prescription that are not redeemed
        # NOTE: group_by with annotate is mainly made if I want to aggreagte and group_by, 
        # here I don't want to aggregate, but simply structure by prescription_ids
        # https://simpleisbetterthancomplex.com/tutorial/2016/12/06/how-to-create-group-by-queries.html
        # So first query prescriptions and then loop through them and get medications per prescription
        non_red_presc_qs = get_list_or_404(
            Prescriptions, 
            patient_id=patient_id,
            redeemed=False,
        )

        # 2. extract information from description
        # TODO: actual extraction, filter -- GPT3/sem search could be embedded here.
        how_to_consume = {
            "time":"twice a day"
        }

        # 3. create return package
        medications = []
        for prescription in non_red_presc_qs: 
            # get all medication associated with the specific prescription
            medications_qs = get_list_or_404(
                Inventory, 
                patientownsmedication__prescription_id=prescription.prescription_id,
            )
            temp = []
            for medication in medications_qs:
                temp.append(
                    {
                        "medication_name":medication.name, 
                        "medication_id":medication.medication_id,
                        "medicationType":medication.medication_type_id.name,
                        "time":how_to_consume["time"],
                        "totalPriceInEur":medication.totalPriceInEUR,
                        "boughtTime":medication.patientownsmedication_set.get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                        "dosageInMg":medication.ppDosageInMg,
                        "totalDosage":medication.totalDosageInMg,
                        "remainingDosage":medication.patientownsmedication_set.get().remainingDosageInMg,
                        "prescription":medication.prescriptionNeeded,
                        "description":medication.description, 
                    }
                )
            # create final package
            medications.append(
                {
                    "prescription_name":prescription.name,
                    "prescription_id":prescription.prescription_id,
                    "doctor_name":prescription.doctor_id.name, 
                    "valid_until":prescription.validUntil.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                    "medications":temp,
                }
            )
        
        return Response(medications, status=status.HTTP_200_OK)

    elif request.method == 'DELETE': 
        return Response("Not implemented yet", status=status.HTTP_204_NO_CONTENT)

    # something went wrong - none of the above cases was called
    return Response("last error", status=status.HTTP_400_BAD_REQUEST)   

@api_view(['POST', 'GET', 'DELETE'])
@parser_classes([JSONParser])
@permission_classes([permissions.AllowAny])
def redeemPrescription(request, format=None):
    """
    Get one or multiple medication ids that were bought via a redeemed prescription.
    Args: 
        medication_ids, array of ints
    Return:
        status ok, 200
    """
    if request.method == 'GET':
        return Response(
            "Not implemented, please specify a patient_id (POST call)", 
            status=status.HTTP_204_NO_CONTENT
        )

    elif request.method == 'POST': 
        ids = request.data["ids"]
        # TODO: set also boughTime to now 
        # TODO: think about scenario when not all medications are redeemed at once
        for id in ids: 
            # assuming there's only one prescription that prescribed a medication 
            # TODO: otherwise the get call throws an error.
            Prescriptions.objects.get(
                patientownsmedication__medication_id=id["medication_id"], 
                patientownsmedication__patient_id=id["patient_id"],
            ).redeemed = True
        
        return Response("Success", status=status.HTTP_200_OK)

    elif request.method == 'DELETE': 
        return Response("Not implemented yet", status=status.HTTP_204_NO_CONTENT)

    # something went wrong - none of the above cases was called
    return Response("last error", status=status.HTTP_400_BAD_REQUEST) 