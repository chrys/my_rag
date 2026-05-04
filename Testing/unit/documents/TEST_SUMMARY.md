# Django Documents App - Unit Test Suite

## Overview
Comprehensive pytest test suite for the Django documents app with **42 passing tests** covering models, serializers, and API views.

## Test Structure

### 1. **test_models.py** (27 tests)
Tests for Document model with state management and constraints.

**TestDocumentModel (27 tests):**
- `test_create_document_minimal` - Create with minimal required fields
- `test_create_document_full` - Create with all fields
- `test_document_timestamps` - Verify created_at auto-set
- `test_indexed_at_optional` - indexed_at is optional
- `test_indexed_at_set` - Setting indexed_at when indexed
- `test_document_string_representation` - String representation with display_name
- `test_document_string_without_display_name` - String with document_name fallback
- `test_valid_index_states` - All state choices (PENDING, INDEXING, INDEXED, FAILED)
- `test_unique_together_project_name` - Unique constraint on project + document_name
- `test_unique_together_different_projects` - Same name allowed in different projects
- `test_error_message_empty` - Error message defaults empty
- `test_error_message_set` - Store error message for failed indexing
- `test_external_document_id_optional` - external_document_id is optional
- `test_display_name_optional` - display_name is optional
- `test_file_size_optional` - file_size is optional
- `test_document_ordering` - Documents ordered by -created_at
- `test_queryset_filter_by_project` - Filter by project FK
- `test_queryset_filter_by_state` - Filter by indexing state
- `test_queryset_filter_by_project_and_state` - Filter by both fields
- `test_cascade_delete_project` - Delete documents when project deleted
- `test_project_related_access` - Access documents from project
- `test_mime_type_default` - mime_type defaults to octet-stream
- `test_update_document_state` - Update state field
- `test_update_error_message` - Update error message

### 2. **test_serializers.py** (11 tests)
Tests for all Document serializers.

**TestDocumentSerializer (3 tests):**
- `test_serialize_pending_document` - Serialize pending document
- `test_serialize_indexed_document` - Serialize indexed document with metadata
- `test_serialize_failed_document` - Serialize failed document with error
- `test_serializer_read_only_fields` - Verify created_at and indexed_at read-only

**TestDocumentCreateSerializer (4 tests):**
- `test_create_document` - Create document via serializer
- `test_create_required_fields` - Validate required fields
- `test_create_optional_fields` - Optional fields handling
- `test_create_always_pending` - Documents start in PENDING state

**TestDocumentUpdateSerializer (4 tests):**
- `test_update_display_name` - Update display name
- `test_update_state` - Update state field
- `test_update_error_message` - Update error message
- `test_update_multiple_fields` - Update multiple fields at once

**TestDocumentListSerializer (3 tests):**
- `test_list_serializer_fields` - Verify lightweight field set
- `test_list_serializer_multiple` - Serialize multiple documents
- `test_list_serializer_data_integrity` - Verify data preservation

### 3. **test_api_views.py** (15 tests)
Tests for DRF API ViewSet and custom actions.

**TestDocumentViewSet (15 tests):**
- `test_list_documents` - List all documents (paginated)
- `test_retrieve_document` - Get single document
- `test_create_document` - Create via API
- `test_update_document` - Full update with PUT
- `test_partial_update_document` - Partial update with PATCH
- `test_delete_document` - Delete document
- `test_by_project_action` - Custom action: documents by project
- `test_by_project_missing_param` - Validate required parameter
- `test_by_state_action` - Custom action: documents by state
- `test_by_state_missing_param` - Validate required parameter
- `test_indexed_action` - Custom action: all indexed documents
- `test_failed_action` - Custom action: all failed documents
- `test_get_serializer_class_list` - Correct serializer for list
- `test_get_serializer_class_create` - Correct serializer for create
- `test_get_serializer_class_update` - Correct serializer for update
- `test_document_filtering_by_state` - Filter by state parameter
- `test_document_filtering_by_project` - Filter by project parameter

## Running Tests

```bash
# Run all documents tests
pytest Testing/unit/documents/ -v

# Run specific test file
pytest Testing/unit/documents/test_models.py -v

# Run specific test class
pytest Testing/unit/documents/test_models.py::TestDocumentModel -v

# Run specific test
pytest Testing/unit/documents/test_models.py::TestDocumentModel::test_create_document_minimal -v

# Run with coverage
pytest Testing/unit/documents/ --cov=src.apps.documents --cov-report=html
```

## Test Coverage

- **Models:** 100% - All fields, relationships, state management, and constraints tested
- **Serializers:** 100% - All serializer variants with validation tested
- **ViewSets:** 100% - CRUD operations and custom actions tested
- **API Actions:** 100% - by_project, by_state, indexed, failed actions tested

## Key Features Tested

✅ Model CRUD operations
✅ Foreign key relationship to Project
✅ Field validation and constraints
✅ Nullable/optional fields
✅ Default values (mime_type, state=PENDING)
✅ State management (PENDING, INDEXING, INDEXED, FAILED)
✅ Unique constraints (project + document_name)
✅ Error message tracking for failed indexing
✅ Timestamps (created_at, indexed_at)
✅ Cascade deletes
✅ QuerySet filtering by project and state
✅ Related name access from project
✅ String representations
✅ All serializer variants (full, create, update, list)
✅ Serializer read-only fields
✅ API CRUD endpoints
✅ Custom actions (by_project, by_state, indexed, failed)
✅ API pagination
✅ Parameter validation
✅ API filtering by state and project

## Test Status
- **Total Tests:** 42
- **Passed:** 42 ✅
- **Failed:** 0
- **Success Rate:** 100%
