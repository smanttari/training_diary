from treenipaivakirja.models import harjoitus
from treenipaivakirja.serializers import HarjoitusSerializer
from django.http import JsonResponse, Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


@api_view(['GET', 'POST'])
@permission_classes((IsAdminUser, ))
def trainings(request):
    """ 
    List all trainings or create a new training.
    """
    if request.method == 'GET':
        trainings = harjoitus.objects.all()
        serializer = HarjoitusSerializer(trainings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = HarjoitusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAdminUser, ))
def trainings_by_id(request,pk):
    """
    Retrieve, update or delete a training.
    """
    try:
        training = harjoitus.objects.get(id=pk)
    except harjoitus.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = HarjoitusSerializer(training)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = HarjoitusSerializer(training, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        training.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)