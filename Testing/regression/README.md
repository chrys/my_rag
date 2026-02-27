# Regression Tests

This directory contains regression tests for previously fixed bugs.

## Test Files

### test_google_file_search_project_creation.py

**Bug Fixed**: 2026-02-27  
**Reporter**: User  
**Description**: Creating a project with `storage_type='google'` would fail silently because the Google File Search API call was commented out in the views.

**Root Cause**: 
- The import for `google_file_search` module was commented out
- The call to `create_new_file_search_store()` was commented out
- No Django database record was created for Google projects

**Fix Applied**:
1. Uncommented the `google_file_search` import
2. Restored the Google File Search store creation functionality
3. Added database record creation for Google projects with proper `external_store_id`
4. Fixed project_id generation to ensure uniqueness using microseconds
5. Updated `get_combined_stores()` to use Django database as source of truth
6. Fixed `delete_project()` to handle both local and Google projects

**Tests Included**:
- `test_create_google_file_search_project_via_post` - Verifies Google projects can be created
- `test_google_project_creation_handles_api_failure` - Verifies graceful failure handling
- `test_google_project_has_unique_project_id` - Ensures uniqueness even with same display names
- `test_local_project_creation_still_works` - Verifies local projects still work
- `test_google_project_deletion_works` - Verifies Google project deletion
- `test_get_combined_stores_includes_google_projects` - Verifies listing includes Google projects
- `test_api_create_google_project_via_serializer` - Verifies DRF API endpoint

### test_custom_prompt_saving.py

**Bug Fixed**: 2026-02-27  
**Reporter**: User  
**Description**: Saving a custom prompt for a project would fail with a 404 error because the API endpoint expected the Django database primary key, but the frontend was sending `external_store_id` which contains slashes for Google projects.

**Error Logs**:
```
Not Found: /api/projects/fileSearchStores/test-google-99oic6yk10ke/prompt
GET /api/projects/fileSearchStores%2Ftest-google-99oic6yk10ke/prompt HTTP/1.1" 404
POST /api/projects/fileSearchStores%2Ftest-google-99oic6yk10ke/prompt HTTP/1.1" 404
```

**Root Cause**:
- The `ProjectViewSet` default lookup was by primary key only
- `get_combined_stores()` was setting `store.name` to `external_store_id` for Google projects
- `external_store_id` contains slashes (e.g., `fileSearchStores/abc-123`) which breaks URL routing
- Even with URL encoding, Django decodes slashes before routing, causing 404s

**Fix Applied**:
1. Override `get_object()` in `ProjectViewSet` to support lookup by pk, project_id, or external_store_id
2. Changed `get_combined_stores()` to always use `project_id` instead of mixing with `external_store_id`
3. Added `documents` action to `ProjectViewSet` for fetching project documents
4. Fixed prompt response format to match frontend expectations (`{'prompt': 'content'}` instead of full serialization)

**Tests Included**:
- `test_save_prompt_for_local_project_by_project_id` - Verify local project prompt saving
- `test_save_prompt_for_google_project_by_project_id` - Verify Google project prompt saving
- `test_retrieve_prompt_by_project_id` - Verify prompt retrieval for local projects
- `test_retrieve_prompt_for_google_project_by_project_id` - Verify prompt retrieval for Google projects
- `test_retrieve_prompt_returns_empty_string_when_no_prompt_exists` - Verify empty prompt handling
- `test_update_existing_prompt` - Verify prompt updates work correctly
- `test_lookup_by_primary_key_still_works` - Verify backward compatibility with pk lookup
- `test_documents_endpoint_with_custom_lookup` - Verify documents endpoint works
- `test_documents_endpoint_for_google_project` - Verify documents for Google projects
- `test_invalid_project_id_returns_404` - Verify proper error handling
- `test_get_prompt_response_format` - Verify GET response format
- `test_post_prompt_response_format` - Verify POST response format

## Running Regression Tests

```bash
# Run all regression tests
pytest Testing/regression/ -v

# Run specific regression test file
pytest Testing/regression/test_google_file_search_project_creation.py -v
pytest Testing/regression/test_custom_prompt_saving.py -v
```

## Adding New Regression Tests

When a bug is fixed:
1. Create a new test file in this directory
2. Name it descriptively: `test_<feature>_<bug_description>.py`
3. Add a module-level docstring explaining the bug and fix
4. Write tests that would have caught the bug
5. Update this README with the new test information
