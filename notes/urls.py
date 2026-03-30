from django.urls import path
from .views import NoteListCreateView, NoteDetailView, S3UploadView

urlpatterns = [
    path('', NoteListCreateView.as_view(), name='note-list-create'),
    path('upload/', S3UploadView.as_view(), name='note-upload'),
    path('<uuid:pk>/', NoteDetailView.as_view(), name='note-detail'),
]
