"""
API models for managing API authentication and usage
"""

import secrets
from django.db import models
from django.contrib.auth.models import User


class APIKey(models.Model):
    """
    API key for programmatic access to the API.
    Scoped per project or user for better token management.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text="The user this API key belongs to"
    )
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='api_keys',
        null=True,
        blank=True,
        help_text="The specific project this API key is authorized for"
    )
    
    key = models.CharField(
        max_length=255,
        unique=True,
        help_text="The API key (keep secret)"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Human-friendly name for this key"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this key is active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this key was used"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        proj_str = f" [{self.project.display_name}]" if self.project else ""
        return f"{self.name}{proj_str} ({self.user.username})"
    
    @staticmethod
    def generate_key():
        """Generate a secure random API key with rag_key_ prefix"""
        return f"rag_key_{secrets.token_urlsafe(28)}"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)


class APIUsage(models.Model):
    """
    Tracks API usage for monitoring and billing purposes.
    """
    
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        help_text="The API key that was used"
    )
    
    endpoint = models.CharField(
        max_length=255,
        help_text="The API endpoint that was called"
    )
    
    method = models.CharField(
        max_length=10,
        help_text="HTTP method (GET, POST, etc.)"
    )
    
    status_code = models.IntegerField(
        help_text="HTTP response status code"
    )
    
    response_time_ms = models.IntegerField(
        help_text="Response time in milliseconds"
    )
    
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the request"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['api_key', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"
