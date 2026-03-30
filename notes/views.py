import os
import boto3
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Note
from .serializers import NoteSerializer

class NoteListCreateView(APIView):
    def get(self, request):
        notes = Note.objects.all()
        serializer = NoteSerializer(notes, many=True)
        return Response({
            "data": serializer.data,
            "message": "Notes retrieved successfully"
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "data": serializer.errors,
                "message": "Validation failed"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({
            "data": serializer.data,
            "message": "Note created successfully"
        }, status=status.HTTP_201_CREATED)

class NoteDetailView(APIView):
    def get_note(self, pk):
        try:
            return Note.objects.get(pk=pk)
        except Note.DoesNotExist:
            return None

    def get(self, request, pk):
        note = self.get_note(pk)
        if not note:
            return Response({
                "data": None,
                "message": "Note not found"
            }, status=status.HTTP_404_NOT_FOUND)
            
        serializer = NoteSerializer(note)
        return Response({
            "data": serializer.data,
            "message": "Note retrieved successfully"
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        note = self.get_note(pk)
        if not note:
            return Response({
                "data": None,
                "message": "Note not found"
            }, status=status.HTTP_404_NOT_FOUND)
            
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                "data": serializer.errors,
                "message": "Validation failed"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        serializer.save()
        return Response({
            "data": serializer.data,
            "message": "Note updated successfully"
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        note = self.get_note(pk)
        if not note:
            return Response({
                "data": None,
                "message": "Note not found"
            }, status=status.HTTP_404_NOT_FOUND)
            
        note.delete()
        return Response({
            "data": None,
            "message": "Note deleted successfully"
        }, status=status.HTTP_200_OK)

class S3UploadView(APIView):
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({
                "data": None,
                "message": "No file provided"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_S3_REGION_NAME')
            )
            bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
            
            # Generate a unique file name
            file_extension = os.path.splitext(file_obj.name)[1]
            unique_filename = f"uploads/{uuid.uuid4()}{file_extension}"
            
            s3_client.upload_fileobj(
                file_obj,
                bucket_name,
                unique_filename,
                ExtraArgs={'ACL': 'public-read', 'ContentType': file_obj.content_type}
            )
            
            region = os.environ.get('AWS_S3_REGION_NAME')
            url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{unique_filename}"
            
            return Response({
                "data": {"url": url},
                "message": "File uploaded successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "data": str(e),
                "message": "Failed to upload file to S3"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
