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
from django.template import loader

from pathlib import Path
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
import os, time, random


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
        # TODO: error handling if resulting queryset is empty
        # 1. get all medication for a patient where dosage >= 0 and already redeemed
        # sorted by daysLeft in ascending order
        medications_qs = Inventory.objects.filter( 
            patientownsmedication__patient_id=patient_id,
            # still medication left, __gt = greater than 
            patientownsmedication__daysLeft__gt=0, 
            # already redeemed
            patientownsmedication__prescription_id__redeemed=True,
        ).order_by("patientownsmedication__daysLeft") 

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
                    "boughtTime":medication.patientownsmedication_set.filter(
                        patient_id=patient_id
                    ).get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                    "dosageInMg":medication.ppDosageInMg,
                    "totalDosage":medication.totalDosageInMg,
                    "daysLeft":medication.patientownsmedication_set.filter(
                        patient_id=patient_id
                    ).get().daysLeft,
                    "totalDays":medication.patientownsmedication_set.filter(
                        patient_id=patient_id
                    ).get().totalDays,
                    "prescription":medication.prescriptionNeeded,
                    "description":medication.description, 
                    "status":medication.patientownsmedication_set.filter(
                        patient_id=patient_id
                    ).get().prescription_id.status,
                    "prescription_id":medication.patientownsmedication_set.filter(
                        patient_id=patient_id
                    ).get().prescription_id.prescription_id,
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
            # TODO: error handling if resulting queryset is empty
            # get all medication associated with the specific prescription
            medications_qs = Inventory.objects.filter( 
                patientownsmedication__prescription_id=prescription.prescription_id,
            ).order_by("patientownsmedication__daysLeft") 

            temp = []
            for medication in medications_qs:
                temp.append(
                    {
                        "medication_name":medication.name, 
                        "medication_id":medication.medication_id,
                        "medicationType":medication.medication_type_id.name,
                        "time":how_to_consume["time"],
                        "totalPriceInEur":medication.totalPriceInEUR,
                        "boughtTime":medication.patientownsmedication_set.filter(
                            patient_id=patient_id
                        ).get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                        "dosageInMg":medication.ppDosageInMg,
                        "totalDosage":medication.totalDosageInMg,
                        "daysLeft":medication.patientownsmedication_set.filter(
                            patient_id=patient_id
                        ).get().daysLeft,
                        "totalDays":medication.patientownsmedication_set.filter(
                            patient_id=patient_id
                        ).get().totalDays,
                        "prescription":medication.prescriptionNeeded,
                        "description":medication.description, 
                        "status":medication.patientownsmedication_set.filter(
                            patient_id=patient_id
                        ).get().prescription_id.status,
                        "prescription_id":medication.patientownsmedication_set.filter(
                            patient_id=patient_id
                        ).get().prescription_id.prescription_id,
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

# Utility function for sending for emails
def send_email_html(subject, text_content, html_content, sender, recipient, image_paths=None, image_names=None):
    email = EmailMultiAlternatives(
        subject=subject, 
        body=text_content, 
        from_email=sender, 
        to=recipient if isinstance(recipient, list) else [recipient]
    )
    for image_path, image_name in zip(image_paths,image_names):
        if all([html_content,image_path,image_name]):
            email.attach_alternative(html_content, "text/html")
            email.content_subtype = 'html'  # set the primary content to be text/html
            email.mixed_subtype = 'related' # it is an important part that ensures embedding of an image 
            with open(image_path, mode='rb') as f:
                image = MIMEImage(f.read())
                email.attach(image)
                image.add_header('Content-ID', f"<{image_name}>")
    return email.send()

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
        # TODO: can I change the displayed name to whatever I want? 
        sender = "nicolas.remerscheid@gmail.com"
        subject = f"Renewal of prescription patient"
        # NOTE: assuming that frontend build up mail body (so that patient can personalize)
        email_body_alternative = f"{email_body}\n\nThe mail doesn't render properly on your device.\n\n \
            Accept: http://{request.META['HTTP_HOST']}/quickstart/api/answer_request/{prescription_id}/accepted\n \
            Call necessary: http://{request.META['HTTP_HOST']}/quickstart/api/answer_request/{prescription_id}/call necessary\n \
            Appointment necessary: http://{request.META['HTTP_HOST']}/quickstart/api/answer_request/{prescription_id}/appointment necessary\n \
            </body></html>"

        # images
        all_img_paths = []
        all_img_names = []
        
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

        logo_path = PROJECT_ROOT+'/templates/assets/img/logo_white_bg.png'
        logo_name = Path(logo_path).name
        # TODO: uncomment if logo is used in mail
        # all_img_paths.append(logo_path)
        # all_img_names.append(logo_name)

        header_path = PROJECT_ROOT+'/templates/assets/img/remedica_header.png'
        header_name = Path(header_path).name
        all_img_paths.append(header_path)
        all_img_names.append(header_name)

        # TODO: the email_body shouldn't contain html tags.
        email_body_html = loader.render_to_string(
            'doctor_mail.html',
            {
                'email_body':email_body,
                'current_domain':request.META['HTTP_HOST'],
                'prescription_id':prescription_id,
                'logo':logo_name,
                'header':header_name,
            }
        )

        # create and send e-mail
        res = send_email_html(
            subject=subject,
            text_content=email_body_alternative, 
            html_content=email_body_html, 
            sender=sender, 
            recipient=doctor.email.split(","), # multiple doctors can be written and seperated by commas
            image_paths=all_img_paths, 
            image_names=all_img_names
        )
        # res = send_mail(
        #     subject=subject, 
        #     message=email_body, 
        #     html_message=email_body_html,
        #     from_email=sender, 
        #     recipient_list=[doctor.email], 
        #     fail_silently=True)

        # set status on pending
        prescription_obj = get_object_or_404(
            Prescriptions, 
            prescription_id=prescription_id,
        )
        prescription_obj.status = "pending"
        prescription_obj.save()
        
        return Response(
            "E-Mail sent!" if res else "There was a problem sending the mail!",
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
        # NOTE: when doing GET request with args from a Frontend for example.
        # prescription_id = request.query_params.get("prescription_id", None)
        # status_str = request.query_params.get("status", None)

        # check if correct params where passed in
        if status_str==None or prescription_id==None: 
            return Response("No status was passed in.", status=status.HTTP_400_BAD_REQUEST)

        prescription_obj = get_object_or_404(
            Prescriptions, 
            prescription_id=prescription_id,
        )

         # NOTE: the if is only for demo participants game 
        victory = False
        if prescription_obj.status=='pending': 
            victory = True
            prescription_obj.status = status_str
            prescription_obj.save()
        
        return HttpResponse(
            f"""
                <html> 
                    <body>
                        <h1 style="font: 30px Arial, sans-serif; text-align:center; color:#236D49;">{status_str}</h1>
                        <p style="font: 15px Arial, sans-serif; text-align:center;">Your response was transfered to the patient</p>
                        <br>
                        <br>
                        <h1 style="font: 30px Arial, sans-serif; text-align:center; color:#ff0000;">{
                            "You won! Are you a doctor?" if victory else "You're too late! But you're still a good doctor ;)"}</h1>
                    </body>
                </html>
            """,
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
                "boughtTime":medication.patientownsmedication_set.filter(
                    patient_id=patient_id
                ).get().boughtTime.strftime("%d-%b-%Y (%H:%M:%S.%f)"),
                "dosageInMg":medication.ppDosageInMg,
                "totalDosage":medication.totalDosageInMg,
                "daysLeft":medication.patientownsmedication_set.filter(
                    patient_id=patient_id
                ).get().daysLeft,
                "totalDays":medication.patientownsmedication_set.filter(
                    patient_id=patient_id
                ).get().totalDays,
                "prescription":medication.prescriptionNeeded,
                "description":medication.description, 
                "status":medication.patientownsmedication_set.filter(
                    patient_id=patient_id
                ).get().prescription_id.status,
                "prescription_id":medication.patientownsmedication_set.filter(
                    patient_id=patient_id
                ).get().prescription_id.prescription_id,
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