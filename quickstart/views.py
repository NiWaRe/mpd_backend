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
def product_explicit(request, format=None):
    """
    TBD
    """
    if request.method == 'GET':
        # assessment_id = request.query_params.get("assessment_id", None)
        products_objs = get_list_or_404(Product)
        products = []
        for prods in products_objs: 
            products.append(
                {
                    "name":prods.name, 
                    "desc":prods.desc, 
                    "prescription":prods.prescription,
                }
            )
        return Response(products, status=status.HTTP_200_OK)

    elif request.method == 'POST': 
        # assessment_id = request.data["assessment_id"]
        pass
        return Response("POST", status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE': 
        pass
        return Response("DELETE", status=status.HTTP_200_OK)

    return Response("last error", status=status.HTTP_400_BAD_REQUEST)   
