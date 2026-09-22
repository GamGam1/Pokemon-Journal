import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import JournalEntry
from unittest.mock import patch

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )


@pytest.fixture
def auth_client(client, user):
    response = client.post('/api/token/', {
        'username': 'testuser',
        'password': 'testpass123'
    }, format='json')
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.fixture
def mock_analyze():
    # mock Claude API so tests don't make real API calls
    with patch('entries.views.analyze_entry') as mock:
        mock.return_value = {
            "themes": ["hopeful"],
            "songs": [{"title": "Pokemon Theme", "artist": "Jason Paige", "game": "Pokemon Anime"}]
        }
        yield mock


# --- AUTH TESTS ---

@pytest.mark.django_db
def test_unauthenticated_request_returns_401(client):
    response = client.get('/api/entries/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_register_creates_user(client):
    response = client.post('/api/register/', {
        'username': 'newuser',
        'password': 'newpass123',
        'email': 'new@test.com'
    }, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username='newuser').exists()


# --- CRUD TESTS ---

@pytest.mark.django_db
def test_authenticated_user_can_create_entry(auth_client, mock_analyze):
    response = auth_client.post('/api/entries/', {
        'content': 'Today was a great day full of hope.'
    }, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['detected_themes'] == ['hopeful']
    assert len(response.data['pokemon_song']) == 1


@pytest.mark.django_db
def test_themes_and_songs_populated_on_create(auth_client, mock_analyze):
    response = auth_client.post('/api/entries/', {
        'content': 'Feeling good today.'
    }, format='json')
    assert response.data['detected_themes'] != []
    assert response.data['pokemon_song'] != []


@pytest.mark.django_db
def test_user_can_only_see_own_entries(client, db):
    # create two users
    user1 = User.objects.create_user(username='user1', password='pass123')
    user2 = User.objects.create_user(username='user2', password='pass123')

    # create entry for user1
    JournalEntry.objects.create(
        user=user1,
        content='User 1 entry',
        detected_themes=['hopeful'],
        pokemon_song=[]
    )

    # log in as user2
    response = client.post('/api/token/', {
        'username': 'user2',
        'password': 'pass123'
    }, format='json')
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # user2 should see empty list
    response = client.get('/api/entries/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


# --- VALIDATION TESTS ---

@pytest.mark.django_db
def test_blank_content_returns_400(auth_client):
    response = auth_client.post('/api/entries/', {
        'content': ''
    }, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_content_over_5000_chars_returns_400(auth_client):
    response = auth_client.post('/api/entries/', {
        'content': 'a' * 5001
    }, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# --- ANALYTICS TESTS ---

@pytest.mark.django_db
def test_patterns_endpoint_returns_theme_frequency(auth_client, user):
    JournalEntry.objects.create(
        user=user,
        content='Entry 1',
        detected_themes=['hopeful', 'determined'],
        pokemon_song=[]
    )
    JournalEntry.objects.create(
        user=user,
        content='Entry 2',
        detected_themes=['hopeful'],
        pokemon_song=[]
    )
    response = auth_client.get('/api/entries/patterns/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_entries'] == 2
    # hopeful appears twice so should be top theme
    assert response.data['top_theme'][0] == 'hopeful'
    assert response.data['top_theme'][1] == 2