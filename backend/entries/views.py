from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JournalEntry
from .serializers import JournalEntrySerializer, UserSerializer
from analysis.tasks import analyze_entry_task
from collections import Counter
from django.core.cache import cache


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
        #claude api, async
        analyze_entry_task.delay(entry.id)
        #bust cache when user adds new entry
        cache.delete(f"patterns_user_{self.request.user.id}")
        
    @action(detail=False, methods=["get"])
    def patterns(self, request):
        cache_key = f"patterns_user_{request.user.id}"
        cached = cache.get(cache_key)

        if cached:
            return Response(cached)

        entries = self.get_queryset()
        all_themes = []
        for entry in entries:
            all_themes.extend(entry.detected_themes)

        theme_counts = Counter(all_themes)
        data = {
            "total_entries": entries.count(),
            "theme_frequency": theme_counts.most_common(),
            "top_theme": theme_counts.most_common(1)[0] if theme_counts else None
        }

        cache.set(cache_key, data, timeout=60 * 15)  # cache for 15 minutes
        return Response(data)
