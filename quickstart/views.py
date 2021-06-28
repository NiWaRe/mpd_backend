from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from django.shortcuts import get_object_or_404, get_list_or_404, render
from rest_framework.decorators import api_view, permission_classes, parser_classes

from quickstart.serializers import *
from quickstart.models import *

from django.http import HttpResponse
from django.core.mail import send_mail


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
            patientownsmedication__daysLeft__gt=0, 
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
                    "daysLeft":medication.patientownsmedication_set.get().daysLeft,
                    "prescription":medication.prescriptionNeeded,
                    "description":medication.description, 
                    "status":medication.patientownsmedication_set.get().prescription_id.status,
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
                        "daysLeft":medication.patientownsmedication_set.get().daysLeft,
                        "prescription":medication.prescriptionNeeded,
                        "description":medication.description, 
                        "status":medication.patientownsmedication_set.get().prescription_id.status,
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
        print(ids)
        for id in ids: 
            # assuming there's only one prescription that prescribed a medication 
            # TODO: otherwise the get call throws an error.
            prescription = get_object_or_404(
                Prescriptions,
                patientownsmedication__medication_id=id["medication_id"], 
                patientownsmedication__patient_id=id["patient_id"],
            )
            prescription.redeemed = True
            prescription.save()
        
        return Response("Success", status=status.HTTP_200_OK)

    elif request.method == 'DELETE': 
        return Response("Not implemented yet", status=status.HTTP_204_NO_CONTENT)

    # something went wrong - none of the above cases was called
    return Response("last error", status=status.HTTP_400_BAD_REQUEST) 

@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([permissions.AllowAny])
def reorderPrescription(request, format=None):
    """
    Kick-Off prescription reordering process with doctor. Auto. send an e-mail with predefined action links 
    to the responsible doctor. 
    Args: 
        doctor_id - int, 
        email_body - str, adapted or predefined mail,
        prescription_id - int
    Return:
        status ok, 200
    """

    if request.method == 'POST': 
        doctor_id = request.data["doctor_id"]
        email_body = request.data["email_body"]
        prescription_id = request.data["prescription_id"]

        # get doctor name, email
        doctor = get_object_or_404(
            Doctors,
            doctor_id=doctor_id,
        )
        
        # TODO: this should be stored and extracted from patient table
        sender = "nicolas.remerscheid@gmail.com"
        subject = f"Renewal of prescription patient"
        # NOTE: assuming that frontend build up mail body (so that patient can personalize)
        email_body_html = f"<html><body>{email_body}<br><br> \
            <a href='http://{request.META['HTTP_HOST']}/quickstart/api/answer_request/{prescription_id}/accepted'> \
                Accept </a> | \
            <a href='http://{request.META['HTTP_HOST']}/quickstart/api/answer_request/{prescription_id}/call necessary'> \
                Call necessary</a> | \
            <a href='http://{request.META['HTTP_HOST']}/quickstart/api/answer_request/{prescription_id}/appointment necessary'> \
                Appointment necessary</a> \
            </body></html>"

        # create and send e-mail
        res = send_mail(
            subject=subject, 
            message=email_body, 
            html_message=email_body_html,
            from_email=sender, 
            recipient_list=[doctor.email], 
            fail_silently=False)
        
        return Response(
            "E-Mail sent!",
            status=status.HTTP_200_OK
        )

    # something went wrong - none of the above cases was called
    return Response("last error", status=status.HTTP_400_BAD_REQUEST) 

@api_view(['GET'])
@parser_classes([JSONParser])
@permission_classes([permissions.AllowAny])
def answerRequest(request, prescription_id, status_str, format=None):
    """
    Called when doctor clicks on specific action link (which was send via mail).
    Args: 
        prescription_id - int, encoded in URL as GET request
        status - str, encoded in URL as GET request
    Return:
        status ok, 200
    """
    if request.method == 'GET':
        # NOTE when doing GET request with args from a Frontend for example.
        # prescription_id = request.query_params.get("prescription_id", None)
        # status_str = request.query_params.get("status", None)

        # check if correct params where passed in
        if status_str==None or prescription_id==None: 
            return Response("No status was passed in.", status=status.HTTP_400_BAD_REQUEST)

        prescription_obj = get_object_or_404(
            Prescriptions, 
            prescription_id=prescription_id,
        )
        prescription_obj.status = status_str
        prescription_obj.save()
        
        return HttpResponse(
            f"<html><body><h1>{status_str}</h1><p>Your response was transfered to the patient</p></body></html>",
            status=status.HTTP_200_OK
        )

    # something went wrong - none of the above cases was called
    return Response("last error", status=status.HTTP_400_BAD_REQUEST) 

@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([permissions.AllowAny])
def responsibleDoctors(request, format=None):
    """
    Get responsible doctors for a certain patient and a certain medication
    Args: 
    {
        patient_id:1,
        medication_ids:[1, 3, 2, ...]
    }
    Return:
    --> for example.
        [
            {
                dr_id: 1,
                dr_name: "nico remerscheid",
                dr_email: "thepresident@tum.ai",
                medicine: [
                    {
                        "medication_name": "Ramipril",
                        "medication_id": 1,
                        "medicationType": "Pill",
                        "time": "twice a day",
                        "totalPriceInEur": 13,
                        "boughtTime": "17-Jun-2021 (20:48:58.000000)",
                        "dosageInMg": 5,
                        "totalDosage": 100,
                        "remainingDosage": 20,
                        "prescription": true,
                        "description": "Works great!"
                    },
                    {...},
                    ...
                ]
            },
            ...
        ]
    """
    if request.method == 'POST':
        patient_id = request.data["patient_id"]
        medication_ids = request.data["medication_ids"]

        # doctor tracking array - for sorting 
        doctor_list = []
        # final package
        doctor_med_packages = []

        for medication_id in medication_ids: 
            # get doctor object 
            doctor = get_object_or_404(
                Doctors, 
                prescriptions__patientownsmedication__medication_id=medication_id, 
                prescriptions__patientownsmedication__patient_id=patient_id,
            )

            # get medication info 
            medication = get_object_or_404(
                Inventory, 
                medication_id=medication_id,
            )

            # TODO: actual extraction, filter -- GPT3/sem search could be embedded here.
            how_to_consume = {
                "time":"twice a day"
            }

            medication_info = {
                "medication_name":medication.name, 
                "medication_id":medication.medication_id,
                "medicationType":medication.medication_type_id.name,
                "time":how_to_consume["time"],
                "totalPriceInEur":medication.totalPriceInEUR,
                "boughtTime":medication.patientownsmedication_set.get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                "dosageInMg":medication.ppDosageInMg,
                "totalDosage":medication.totalDosageInMg,
                "daysLeft":medication.patientownsmedication_set.get().daysLeft,
                "prescription":medication.prescriptionNeeded,
                "description":medication.description,
                "status":medication.patientownsmedication_set.get().prescription_id.status,
            }

            # two cases - for sorting (sql group by would've been the easiest)
            if not doctor.doctor_id in doctor_list: 
                # 1.case: create new entry 
                doctor_list.append(doctor.doctor_id)
                doctor_med_packages.append(
                    {
                        "dr_id": doctor.doctor_id,
                        "dr_name": doctor.name,
                        "dr_email": doctor.email,
                        "medicine": [medication_info],
                     }
                )
            else: 
                # TODO: this is very condensed but also not very readable
                # 2.case: append-case
                doctor_med_packages[doctor_list==doctor.doctor_id]["medicine"].append(
                    medication_info,
                )
        
        return Response(
            doctor_med_packages,
            status=status.HTTP_200_OK
        )

    # something went wrong - none of the above cases was called
    return Response("last error", status=status.HTTP_400_BAD_REQUEST) 