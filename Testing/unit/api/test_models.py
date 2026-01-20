"""
Unit tests for API app models
"""

import pytest
from django.contrib.auth.models import User
from apps.api.models import APIKey, APIUsage


@pytest.mark.django_db
class TestAPIKeyModel:
    """Tests for APIKey model"""
    
    @pytest.fixture
    def user(self):
        """Create a test user"""
        return User.objects.create_user(username='testuser', password='testpass')
    
    def test_create_api_key(self, user):
        """Test creating an API key"""
        api_key = APIKey.objects.create(
            user=user,
            name='Test Key',
            key='test_key_12345'
        )
        
        assert api_key.id is not None
        assert api_key.user == user
        assert api_key.name == 'Test Key'
        assert api_key.is_active is True
    
    def test_api_key_default_active(self, user):
        """Test that API keys are active by default"""
        api_key = APIKey.objects.create(
            user=user,
            name='Test Key',
            key='test_key'
        )
        
        assert api_key.is_active is True
    
    def test_api_key_inactive(self, user):
        """Test creating an inactive API key"""
        api_key = APIKey.objects.create(
            user=user,
            name='Inactive Key',
            key='inactive_key',
            is_active=False
        )
        
        assert api_key.is_active is False
    
    def test_api_key_unique_constraint(self, user):
        """Test that API keys are unique"""
        APIKey.objects.create(
            user=user,
            name='Key 1',
            key='unique_key_123'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            APIKey.objects.create(
                user=user,
                name='Key 2',
                key='unique_key_123'  # Duplicate
            )
    
    def test_api_key_str_representation(self, user):
        """Test string representation"""
        api_key = APIKey.objects.create(
            user=user,
            name='My Key',
            key='some_key'
        )
        
        assert str(api_key) == f"My Key ({user.username})"
    
    def test_api_key_timestamps(self, user):
        """Test that timestamps are set correctly"""
        api_key = APIKey.objects.create(
            user=user,
            name='Test Key',
            key='test_key'
        )
        
        assert api_key.created_at is not None
        assert api_key.last_used_at is None
    
    def test_api_key_update_last_used(self, user):
        """Test updating last_used_at"""
        api_key = APIKey.objects.create(
            user=user,
            name='Test Key',
            key='test_key'
        )
        
        from django.utils import timezone
        now = timezone.now()
        api_key.last_used_at = now
        api_key.save()
        
        api_key.refresh_from_db()
        assert api_key.last_used_at is not None
    
    def test_api_key_ordering(self, user):
        """Test that API keys are ordered by created_at descending"""
        key1 = APIKey.objects.create(
            user=user,
            name='Key 1',
            key='key_1'
        )
        key2 = APIKey.objects.create(
            user=user,
            name='Key 2',
            key='key_2'
        )
        
        keys = list(APIKey.objects.all())
        assert keys[0].id == key2.id
        assert keys[1].id == key1.id
    
    def test_cascade_delete_on_user(self, user):
        """Test cascade delete when user is deleted"""
        api_key = APIKey.objects.create(
            user=user,
            name='Test Key',
            key='test_key'
        )
        
        key_id = api_key.id
        user.delete()
        
        assert not APIKey.objects.filter(id=key_id).exists()
    
    def test_generate_key_static_method(self):
        """Test key generation method"""
        key1 = APIKey.generate_key()
        key2 = APIKey.generate_key()
        
        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert len(key1) > 0
        assert len(key2) > 0
        assert key1 != key2  # Should be unique
    
    def test_multiple_keys_per_user(self, user):
        """Test that a user can have multiple API keys"""
        key1 = APIKey.objects.create(
            user=user,
            name='Key 1',
            key='key_1'
        )
        key2 = APIKey.objects.create(
            user=user,
            name='Key 2',
            key='key_2'
        )
        
        user_keys = APIKey.objects.filter(user=user)
        assert len(user_keys) == 2
    
    def test_different_users_different_keys(self):
        """Test that different users have separate keys"""
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')
        
        key1 = APIKey.objects.create(
            user=user1,
            name='User 1 Key',
            key='key_1'
        )
        key2 = APIKey.objects.create(
            user=user2,
            name='User 2 Key',
            key='key_2'
        )
        
        assert key1.user != key2.user
        assert APIKey.objects.filter(user=user1).count() == 1
        assert APIKey.objects.filter(user=user2).count() == 1


@pytest.mark.django_db
class TestAPIUsageModel:
    """Tests for APIUsage model"""
    
    @pytest.fixture
    def user(self):
        """Create a test user"""
        return User.objects.create_user(username='testuser', password='testpass')
    
    @pytest.fixture
    def api_key(self, user):
        """Create a test API key"""
        return APIKey.objects.create(
            user=user,
            name='Test Key',
            key='test_key'
        )
    
    def test_create_api_usage(self, api_key):
        """Test creating an API usage log"""
        usage = APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=150,
            ip_address='192.168.1.1'
        )
        
        assert usage.id is not None
        assert usage.api_key == api_key
        assert usage.endpoint == '/api/projects/'
        assert usage.method == 'GET'
        assert usage.status_code == 200
    
    def test_api_usage_various_methods(self, api_key):
        """Test recording different HTTP methods"""
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        
        for method in methods:
            usage = APIUsage.objects.create(
                api_key=api_key,
                endpoint='/api/projects/',
                method=method,
                status_code=200,
                response_time_ms=100,
                ip_address='192.168.1.1'
            )
            
            assert usage.method == method
    
    def test_api_usage_various_status_codes(self, api_key):
        """Test recording different status codes"""
        status_codes = [200, 201, 400, 404, 500]
        
        for code in status_codes:
            usage = APIUsage.objects.create(
                api_key=api_key,
                endpoint='/api/projects/',
                method='GET',
                status_code=code,
                response_time_ms=100,
                ip_address='192.168.1.1'
            )
            
            assert usage.status_code == code
    
    def test_api_usage_str_representation(self, api_key):
        """Test string representation"""
        usage = APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=150,
            ip_address='192.168.1.1'
        )
        
        assert str(usage) == "GET /api/projects/ - 200"
    
    def test_api_usage_timestamp(self, api_key):
        """Test that created_at is set"""
        usage = APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=150,
            ip_address='192.168.1.1'
        )
        
        assert usage.created_at is not None
    
    def test_api_usage_cascade_delete_on_key(self, api_key):
        """Test cascade delete when API key is deleted"""
        usage = APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=150,
            ip_address='192.168.1.1'
        )
        
        usage_id = usage.id
        api_key.delete()
        
        assert not APIUsage.objects.filter(id=usage_id).exists()
    
    def test_api_usage_ordering(self, api_key):
        """Test that usage logs are ordered by created_at descending"""
        usage1 = APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=100,
            ip_address='192.168.1.1'
        )
        usage2 = APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/chat/',
            method='POST',
            status_code=201,
            response_time_ms=200,
            ip_address='192.168.1.2'
        )
        
        usage_logs = list(APIUsage.objects.all())
        assert usage_logs[0].id == usage2.id
        assert usage_logs[1].id == usage1.id
    
    def test_filter_by_api_key(self, user, api_key):
        """Test filtering usage by API key"""
        other_user = User.objects.create_user(username='other', password='pass')
        other_key = APIKey.objects.create(
            user=other_user,
            name='Other Key',
            key='other_key'
        )
        
        usage1 = APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=100,
            ip_address='192.168.1.1'
        )
        usage2 = APIUsage.objects.create(
            api_key=other_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=100,
            ip_address='192.168.1.1'
        )
        
        key_usage = APIUsage.objects.filter(api_key=api_key)
        assert len(key_usage) == 1
        assert key_usage[0].id == usage1.id
    
    def test_filter_by_status_code(self, api_key):
        """Test filtering by status code"""
        APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=100,
            ip_address='192.168.1.1'
        )
        APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=404,
            response_time_ms=50,
            ip_address='192.168.1.1'
        )
        
        errors = APIUsage.objects.filter(status_code__gte=400)
        assert len(errors) == 1
    
    def test_filter_by_endpoint(self, api_key):
        """Test filtering by endpoint"""
        APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/projects/',
            method='GET',
            status_code=200,
            response_time_ms=100,
            ip_address='192.168.1.1'
        )
        APIUsage.objects.create(
            api_key=api_key,
            endpoint='/api/chat/',
            method='GET',
            status_code=200,
            response_time_ms=150,
            ip_address='192.168.1.1'
        )
        
        project_usage = APIUsage.objects.filter(endpoint='/api/projects/')
        assert len(project_usage) == 1
    
    def test_multiple_usage_logs_per_key(self, api_key):
        """Test that an API key can have multiple usage logs"""
        for i in range(5):
            APIUsage.objects.create(
                api_key=api_key,
                endpoint='/api/projects/',
                method='GET',
                status_code=200,
                response_time_ms=100,
                ip_address='192.168.1.1'
            )
        
        usage_logs = APIUsage.objects.filter(api_key=api_key)
        assert len(usage_logs) == 5
