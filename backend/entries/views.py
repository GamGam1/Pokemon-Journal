from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JournalEntry
from .serializers import JournalEntrySerializer, UserSerializer
from analysis.services import analyze_entry
from collections import Counter


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
    
    @action(detail=False, methods=["get"])
    def patterns(self, request):
        entries = self.get_queryset()
        
        # flatten all themes from all entries into one list
        all_themes = []
        for entry in entries:
            all_themes.extend(entry.detected_themes)
        
        # count frequency of each theme
        theme_counts = Counter(all_themes)
        
        return Response({
            "total_entries": entries.count(),
            "theme_frequency": theme_counts.most_common(),
            "top_theme": theme_counts.most_common(1)[0] if theme_counts else None
        })
