from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JournalEntry
from .serializers import JournalEntrySerializer, UserSerializer
from analysis.services import analyze_entry


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # only public endpoint


class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # users only ever see their own entries
        return JournalEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # automatically attach the logged-in user on save
        entry = serializer.save(user=self.request.user)
        #claude api
        result = analyze_entry(entry.content)
        entry.detected_themes = result["themes"]
        entry.pokemon_song = result["songs"]  # now a list
        entry.save()
