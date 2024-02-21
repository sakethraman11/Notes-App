from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .models import Note, NoteVersion
from .serializers import NoteSerializer, NoteVersionSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')

            # Check for duplicate username
            if User.objects.filter(username=username).exists():
                return Response({'error': 'A user with that username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check for duplicate email
            if User.objects.filter(email=email).exists():
                return Response({'error': 'A user with that email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # Save the user
            serializer.save()
            return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
        else:
            # Check for missing email field
            if 'email' in serializer.errors:
                return Response({'error': 'Email field is required.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Please use a POST request to sign up.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Please use a POST request to authenticate.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_note(request):
    if request.method == 'POST':
        serializer = NoteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message': 'Note created successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Please use a POST request to create a note.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_note(request, id):
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)

    if note.user == request.user or request.user in note.shared_with.all():
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    else:
        return Response({'error': 'You do not have permission to access this note.'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def share_note(request):
    note_id = request.data.get('note_id')
    users_to_share_with = request.data.get('users')

    try:
        note = Note.objects.get(id=note_id)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)

    if note.user != request.user:
        return Response({'error': 'You do not have permission to share this note.'}, status=status.HTTP_403_FORBIDDEN)

    for username in users_to_share_with:
        try:
            user = User.objects.get(username=username)
            note.shared_with.add(user)
        except User.DoesNotExist:
            return Response({'error': f'User {username} not found.'}, status=status.HTTP_404_NOT_FOUND)

    note.save()

    return Response({'message': 'Note shared successfully.'}, status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_note(request, id):
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has permission to edit the note
    if not request.user == note.user and request.user not in note.shared_with.all():
        return Response({'error': 'You do not have permission to edit this note.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = NoteSerializer(note, data=request.data)
    if serializer.is_valid():
        # Save the updated note
        serializer.save()

        # Create a new NoteVersion entry to track the change
        NoteVersion.objects.create(note=note, content=note.content)

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_note_version_history(request, id):
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)

    if note.user != request.user and request.user not in note.shared_with.all():
        return Response({'error': 'You do not have permission to access the version history of this note.'}, status=status.HTTP_403_FORBIDDEN)

    versions = note.noteversion_set.all()
    serializer = NoteVersionSerializer(versions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])  # Define a new view for deleting notes
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsOwnerOrReadOnly])  # Add permission check
def delete_note(request, id):
    try:
        note = Note.objects.get(id=id)
    except Note.DoesNotExist:
        return Response({'error': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)

    note.delete()
    return Response({'message': 'Note deleted successfully.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def home(request):
    return JsonResponse({'message': 'Welcome to the home page.'}, status=status.HTTP_200_OK)
