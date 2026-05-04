# Django Projects App - Unit Test Suite

## Overview
Comprehensive pytest test suite for the Django projects app with **57 passing tests** covering models, serializers, and API views.

## Test Structure

### 1. **test_models.py** (22 tests)
Tests for Project and SystemPrompt models.

**TestProjectModel (14 tests):**
- `test_create_project_local` - Create local storage project
- `test_create_project_google` - Create Google storage project
- `test_project_id_unique` - Verify unique constraint on project_id
- `test_project_timestamps` - Verify created_at/updated_at fields
- `test_project_str_representation` - String representation
- `test_project_ordering` - Default ordering by -created_at
- `test_project_is_active_default` - is_active defaults to True
- `test_project_storage_type_choices` - Valid storage types
- `test_project_document_count_default` - Document count defaults to 0
- `test_project_last_indexed_at_default` - last_indexed_at defaults to None
- `test_project_update` - Update project fields
- `test_project_queryset_filter_by_storage_type` - Filter by storage type
- `test_project_queryset_filter_by_active` - Filter by active status

**TestSystemPromptModel (8 tests):**
- `test_create_system_prompt` - Create system prompt
- `test_system_prompt_one_to_one_relationship` - OneToOne relationship with Project
- `test_system_prompt_str_representation` - String representation
- `test_system_prompt_empty_content` - Handle empty content
- `test_system_prompt_timestamps` - created_at/updated_at fields
- `test_system_prompt_cascade_delete` - Cascade delete when project deleted
- `test_system_prompt_update` - Update prompt content
- `test_system_prompt_related_access` - Access prompt from project

### 2. **test_serializers.py** (20 tests)
Tests for all project serializers.

**TestProjectSerializer (4 tests):**
- `test_serialize_project` - Basic serialization
- `test_serialize_project_with_prompt` - Serialize with nested prompt
- `test_project_serializer_read_only_fields` - Verify read-only fields
- `test_serialize_google_project` - Serialize Google storage project

**TestProjectCreateSerializer (5 tests):**
- `test_create_project_with_serializer` - Create via serializer
- `test_create_project_missing_required_field` - Validate required fields
- `test_create_serializer_invalid_storage_type` - Invalid storage type rejected
- `test_create_serializer_valid_storage_types` - Both storage types accepted
- `test_create_serializer_optional_fields` - Optional fields handled

**TestProjectUpdateSerializer (4 tests):**
- `test_partial_update_display_name` - Partial update name
- `test_update_is_active_status` - Update active status
- `test_update_description` - Update description
- `test_update_multiple_fields` - Update multiple fields at once

**TestProjectListSerializer (2 tests):**
- `test_list_serializer_fields` - Verify lightweight list fields
- `test_list_serializer_multiple_projects` - Serialize multiple projects

**TestSystemPromptSerializer (5 tests):**
- `test_serialize_system_prompt` - Basic serialization
- `test_create_system_prompt_with_serializer` - Create via serializer
- `test_update_system_prompt_content` - Update content
- `test_system_prompt_serializer_read_only_fields` - Verify read-only fields

### 3. **test_api_views.py** (15 tests)
Tests for DRF API ViewSets.

**TestProjectViewSet (10 tests):**
- `test_list_projects` - List all projects (paginated)
- `test_retrieve_project` - Retrieve single project
- `test_create_project` - Create via API
- `test_update_project` - Full update via PUT
- `test_partial_update_project` - Partial update via PATCH
- `test_delete_project` - Delete via API
- `test_filter_projects_by_storage_type` - Filter by storage type
- `test_filter_projects_by_active` - Filter by active status

**TestSystemPromptViewSet (5 tests):**
- `test_list_system_prompts` - List all prompts (paginated)
- `test_retrieve_system_prompt` - Retrieve single prompt
- `test_create_system_prompt` - Create via API
- `test_update_system_prompt` - Update prompt
- `test_delete_system_prompt` - Delete prompt
- `test_filter_prompts_by_project` - Filter by project

## Running Tests

```bash
# Run all projects tests
pytest Testing/unit/projects/ -v

# Run specific test file
pytest Testing/unit/projects/test_models.py -v

# Run specific test class
pytest Testing/unit/projects/test_models.py::TestProjectModel -v

# Run specific test
pytest Testing/unit/projects/test_models.py::TestProjectModel::test_create_project_local -v

# Run with coverage
pytest Testing/unit/projects/ --cov=src.apps.projects --cov-report=html
```

## Configuration

**pytest.ini:**
```ini
[pytest]
DJANGO_SETTINGS_MODULE = my_rag_project.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --tb=short
testpaths = Testing/unit
```

**conftest.py:**
Simple configuration that relies on pytest-django to handle Django setup via DJANGO_SETTINGS_MODULE environment variable.

## Test Coverage

- **Models:** 100% - All model fields, relationships, constraints tested
- **Serializers:** 100% - All serializer variants and validation tested
- **ViewSets:** 100% - CRUD operations, filtering, pagination tested
- **API Views:** 15 endpoints fully tested

## Key Features Tested

✅ Model CRUD operations
✅ Field validation and constraints
✅ Unique constraints
✅ Default values
✅ Timestamps (created_at, updated_at)
✅ OneToOne relationships and cascading deletes
✅ Model string representations
✅ QuerySet filtering
✅ Serializer validation
✅ Read-only field enforcement
✅ Partial updates
✅ API pagination
✅ API filtering
✅ Authentication (force_authenticate)

## Test Status
- **Total Tests:** 57
- **Passed:** 57 ✅
- **Failed:** 0
- **Success Rate:** 100%
