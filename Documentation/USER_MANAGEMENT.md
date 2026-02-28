# User Management Documentation

## Overview
My RAG implements a multi-tenant user management system using Django's built-in authentication framework. This ensures that users can securely manage their own projects, documents, and chat histories without interfering with others.

## Authentication

### UI Authentication
- Users can authenticate via the standard login page (`/accounts/login/`).
- The login view uses the custom template located at `templates/registration/login.html`.
- Upon successful authentication, the UI dashboard will conditionally render user-specific controls (e.g., displaying the username and a logout button).
- Unauthenticated users will be prompted to log in.

### API Authentication
- The REST API utilizes `SessionAuthentication` and `BasicAuthentication` (as provided by DRF defaults).
- Core endpoints (like `/api/projects/`) are protected using the `IsAuthenticated` permission class, meaning all requests must include valid session or token credentials.

## Project Isolation

Data isolation is a key feature of the user management implementation:
- **Project Ownership:** The `Project` model includes a `user` ForeignKey. Every time a new project is created via the UI or API, it is automatically assigned to the currently authenticated user.
- **API Filtering:** The `ProjectViewSet` automatically filters the returned queryset based on `request.user`. Users will *only* receive their own projects when calling `GET /api/projects/`.
- **UI Filtering:** The `get_combined_stores()` utility function in `apps/projects/views.py` has been updated to filter backend projects based on the authenticated user before rendering the HTML dashboard.

## Next Steps / Future Enhancements
- Implementation of a user registration flow (`/accounts/register/`).
- Role-based access control (RBAC) to allow "Admin" users to view all projects across the platform.
- Token-based authentication (e.g., JWT) for external API clients.