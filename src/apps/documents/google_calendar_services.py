"""
Google Calendar Service Engine for OAuth token exchange, API event fetching,
YAML frontmatter Markdown generation, and background sync/indexing lifecycles.
"""

import os
import glob
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone as dt_timezone
from django.conf import settings
from django.utils import timezone
from django.utils.text import get_valid_filename
from src.apps.documents.models import GoogleCalendarSource, GoogleCalendarEvent


def get_google_client_config() -> dict:
    """Read and return client credentials dictionary from git_ignore/client_secret_*.json."""
    base_dir = getattr(settings, 'BASE_DIR', os.getcwd())
    secret_files = glob.glob(os.path.join(base_dir, 'git_ignore', 'client_secret_*.json'))
    if not secret_files:
        # Fallback search in project root if executed from subfolder
        secret_files = glob.glob(os.path.join(base_dir, '..', 'git_ignore', 'client_secret_*.json'))

    if not secret_files:
        raise FileNotFoundError("Google OAuth client secret file not found under git_ignore/ directory")

    with open(secret_files[0], 'r', encoding='utf-8') as f:
        data = json.load(f)

    web_config = data.get('web', {})
    return {
        'client_id': web_config.get('client_id', ''),
        'client_secret': web_config.get('client_secret', ''),
        'auth_uri': web_config.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth'),
        'token_uri': web_config.get('token_uri', 'https://oauth2.googleapis.com/token'),
    }


def get_oauth_authorization_url(project_id: str, redirect_uri: str = "http://127.0.0.1:8000/rag/google/oauth2callback/") -> str:
    """Construct Google OAuth2 authorization URL with required calendar scopes."""
    config = get_google_client_config()
    params = {
        'client_id': config['client_id'],
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/calendar.readonly',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': project_id,
    }
    return f"{config['auth_uri']}?{urllib.parse.urlencode(params)}"


def exchange_oauth_code_for_tokens(code: str, redirect_uri: str = "http://127.0.0.1:8000/rag/google/oauth2callback/") -> dict:
    """Exchange authorization code for access and refresh tokens."""
    config = get_google_client_config()
    payload = urllib.parse.urlencode({
        'code': code,
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }).encode('utf-8')

    req = urllib.request.Request(config['token_uri'], data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        return body


def refresh_oauth_access_token(source: GoogleCalendarSource) -> str:
    """Refresh expired access token using stored refresh token."""
    if not source.refresh_token:
        return source.access_token

    config = get_google_client_config()
    payload = urllib.parse.urlencode({
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'refresh_token': source.refresh_token,
        'grant_type': 'refresh_token',
    }).encode('utf-8')

    req = urllib.request.Request(config['token_uri'], data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode('utf-8'))
        access_token = body.get('access_token', '')
        if access_token:
            source.access_token = access_token
            source.save()
        return access_token


def convert_event_to_markdown(event: dict, store_id: str, base_dir: str = None) -> tuple[str, str, str]:
    """
    Convert Google Calendar API event dict into structured Markdown with YAML frontmatter.
    Returns tuple of (relative_path, absolute_file_path, markdown_content).
    """
    event_id = event.get('id', 'unknown_event')
    summary = event.get('summary', 'Untitled Event').strip()
    description = event.get('description', '').strip()

    start_dict = event.get('start', {})
    start_str = start_dict.get('dateTime') or start_dict.get('date', '')
    end_dict = event.get('end', {})
    end_str = end_dict.get('dateTime') or end_dict.get('date', '')

    organizer = event.get('organizer', {}).get('email', '')
    attendees = [att.get('email', '') for att in event.get('attendees', []) if att.get('email')]
    location = event.get('location', '')

    date_prefix = start_str[:10] if start_str else datetime.now().strftime('%Y-%m-%d')
    safe_title = re.sub(r'[^\w\s-]', '', summary).strip().replace(' ', '_')[:50] or 'Event'
    file_name = f"{date_prefix}_{safe_title}.md"
    rel_path = f"Calendar/{file_name}"

    base_path = base_dir or getattr(settings, 'BASE_DIR', os.getcwd())
    calendar_dir = os.path.join(base_path, 'rag_data', store_id, 'Calendar')
    os.makedirs(calendar_dir, exist_ok=True)
    full_path = os.path.join(calendar_dir, file_name)

    attendees_yaml = json.dumps(attendees)
    markdown_content = f"""---
event_id: "{event_id}"
summary: "{summary}"
start_time: "{start_str}"
end_time: "{end_str}"
organizer: "{organizer}"
attendees: {attendees_yaml}
location: "{location}"
status: "PENDING"
---

# {summary}

**Date & Time:** {start_str} to {end_str}  
**Organizer:** {organizer}  
**Location:** {location or 'N/A'}  
**Attendees:** {', '.join(attendees) if attendees else 'None'}  

## Event Details
{description or 'No description provided.'}
"""

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return rel_path, full_path, markdown_content


def fetch_events_from_google_api(source: GoogleCalendarSource) -> list[dict]:
    """Fetch calendar events from Google Calendar API."""
    if not source.access_token:
        return []

    calendars = source.selected_calendars or ['primary']
    all_events = []

    for cal_id in calendars:
        url = f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(cal_id)}/events?maxResults=250"
        req = urllib.request.Request(url, headers={'Authorization': f"Bearer {source.access_token}"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                items = data.get('items', [])
                all_events.extend(items)
        except Exception as e:
            # Try refreshing token if HTTP 401
            if '401' in str(e):
                new_token = refresh_oauth_access_token(source)
                if new_token:
                    req = urllib.request.Request(url, headers={'Authorization': f"Bearer {new_token}"})
                    with urllib.request.urlopen(req) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                        items = data.get('items', [])
                        all_events.extend(items)

    return all_events


def run_google_calendar_sync_lifecycle(source: GoogleCalendarSource, mode: str = 'sync', base_dir: str = None) -> dict:
    """Execute calendar sync lifecycle: fetches API events, updates Markdown files, creates DB tracking records."""
    source.sync_status = 'SYNCING'
    source.save()

    try:
        events = fetch_events_from_google_api(source)
        store_id = source.project.project_id

        for evt in events:
            evt_id = evt.get('id')
            summary = evt.get('summary', 'Untitled Event')
            if not evt_id:
                continue

            rel_path, full_path, _ = convert_event_to_markdown(evt, store_id=store_id, base_dir=base_dir)

            GoogleCalendarEvent.objects.update_or_create(
                calendar_source=source,
                event_id=evt_id,
                defaults={
                    'summary': summary,
                    'relative_path': rel_path,
                    'status': 'PENDING',
                }
            )

        total_count = source.events.count()
        pending_count = source.events.filter(status='PENDING').count()
        indexed_count = source.events.filter(status='INDEXED').count()
        failed_count = source.events.filter(status='FAILED').count()

        source.total_events_count = total_count
        source.pending_events_count = pending_count
        source.indexed_events_count = indexed_count
        source.failed_events_count = failed_count
        source.sync_status = 'COMPLETED'
        source.save()

        return {
            'total_events': total_count,
            'pending_events': pending_count,
            'indexed_events': indexed_count,
            'failed_events': failed_count,
        }
    except Exception as exc:
        source.sync_status = 'FAILED'
        source.error_message = str(exc)
        source.save()
        raise exc
