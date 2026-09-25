# DocManager

A Django-based Document Management System for organizing people, document types, uploaded documents, document tracking, and document lifecycle management through a centralized web interface.

## Overview

DocManager is designed to help organizations manage documents associated with students, employees, or other registered people.

The system provides:

- Person management
- Person-wise document tracking
- Configurable document types
- Document upload and management
- Search and filtering
- Document completion tracking
- Recent document viewing
- Trash and restore functionality
- Permanent document deletion
- Django authentication
- Superuser and normal-user access control
- Administrative settings

## Features

### Dashboard

The dashboard provides an overview of the document-management system, including:

- Total people
- Document statistics
- Recent uploads
- Logged-in user information
- Document activity
- Completion information

### People Management

Users can register and manage people with information such as:

- Person ID
- Name
- Email
- Phone
- Person Type
- Department
- Created Date

Supported person categories can include:

- Student
- Employee

### Person Profile

Each person has a dedicated profile showing:

- Personal information
- Required documents
- Submitted documents
- Missing documents
- Completion percentage

The required documents are determined according to the person's type and active document-type configuration.

### Document Management

The Documents section acts as the central file manager.

It supports:

- Uploading documents
- Viewing documents
- Searching documents
- Filtering by document type
- Filtering by person type
- Filtering by status
- Moving documents to Trash

Documents are associated with both a person and a document type.

### Document Types

Document Types define the categories used to organize uploaded documents.

Examples include:

- Identity Document
- Tax Document
- Educational Certificate
- Other organization-specific document categories

A document type can contain:

- Name
- Description
- Allowed file types
- Required for
- Active/inactive status

Document requirements can be configured for:

- Students
- Employees
- Both

### Document Completion Tracking

DocManager calculates document completion dynamically.

For example:

```text
Required documents: 5
Submitted documents: 4
Missing documents: 1
Completion: 80%
```

### Recent Documents

The Recent Documents section provides quick access to recently uploaded active documents.

The current implementation displays the latest 20 documents.

### Trash and Restore

DocManager uses soft deletion for documents.

When a document is moved to Trash, it is marked as deleted rather than immediately removed from the database.

Workflow:

```text
Active Document
      ↓
Move to Trash
      ↓
Trash
   ┌──┴──────────────┐
Restore        Permanent Delete
```

Restoring a document returns it to the active document list.

Permanent deletion removes the uploaded file and its database record.

## Authentication and User Roles

DocManager uses Django's built-in authentication system.

### Superuser

The superuser is created through Django's command line:

```bash
python manage.py createsuperuser
```

The superuser has full control over the DocManager system, including:

- People
- Documents
- Document Types
- Trash
- Normal project users
- Settings

### Normal User

Normal users are created by an authorized superuser through the application's user-management section.

Normal users can use the regular DocManager features but cannot manage project users or create superusers.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| HTML5 | Page structure |
| CSS3 | Interface styling |
| JavaScript | Client-side interactions |
| Bootstrap Icons | UI icons |
| SQLite | Development database |
| Django ORM | Database operations |
| Django Authentication | Authentication and user management |
| FileField / Media | Uploaded document storage |
| Git | Version control |
| GitHub | Source-code hosting |

## Architecture

DocManager follows Django's MVT architecture:

```text
User
  ↓
Web Browser
  ↓
Django URL Routing
  ↓
Views
  ├── Forms
  └── Models
          ↓
       Database
  ↓
Templates
  ↓
HTML / CSS / JavaScript
```

## Database Design

The main entities are:

### Person

```text
id
person_id
name
email
phone
person_type
department
created_at
```

### DocumentType

```text
id
name
description
allowed_file_types
required_for
is_active
```

### Document

```text
id
person_id
document_type_id
file
status
uploaded_at
is_deleted
deleted_at
```

### Relationships

```text
Person
  │
  └──< Documents >── DocumentType
```

A person can have multiple documents.

Each document belongs to one person and one document type.

A document type can be associated with multiple documents.

## Search and Filtering

The Documents section supports searching across information such as:

- File name/path
- Person name
- Person ID
- Document type

Available filters include:

- Document Type
- Person Type
- Status

## Project Structure

```text
DocManagement/
│
├── manage.py
│
├── DocManagement/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── DocManager/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── media/
│   └── documents/
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Main Application Sections

```text
Dashboard
│
├── People
│   ├── Add Person
│   └── Person Profile
│       └── Upload Document
│
├── Documents
│   └── All Documents
│
├── Recent
│
├── Document Types
│   ├── Add
│   ├── Edit
│   ├── Activate/Deactivate
│   └── Delete
│
├── Trash
│   ├── Restore
│   └── Permanent Delete
│
└── Settings
    ├── My Profile
    ├── Users
    ├── Security
    └── About
```

## URL Structure

| URL | Purpose |
|---|---|
| `/` | Login |
| `/logout/` | Logout |
| `/dashboard/` | Dashboard |
| `/people/` | People |
| `/people/add/` | Add Person |
| `/people/<id>/` | Person Profile |
| `/people/<id>/upload/` | Person-specific document upload |
| `/documents/` | All Documents |
| `/documents/upload/` | General document upload |
| `/recent/` | Recent Documents |
| `/document-types/` | Document Types |
| `/trash/` | Trash |
| `/settings/` | Settings |

## Document Storage

Uploaded documents are stored in Django's media directory:

```text
media/documents/
```

The `media/` directory should **not** be committed to a public GitHub repository because it may contain private uploaded documents.

The project `.gitignore` should include:

```gitignore
media/
.env
db.sqlite3
__pycache__/
*.pyc
.vscode/
staticfiles/
```

## Typical Workflow

```text
1. Create the superuser
        ↓
2. Log in
        ↓
3. Configure Document Types
        ↓
4. Create normal project users
        ↓
5. Add People
        ↓
6. Open a Person Profile
        ↓
7. Upload required documents
        ↓
8. Monitor document completion
        ↓
9. Search and filter documents
        ↓
10. Manage deleted documents through Trash
```

## Security Considerations

DocManager is intended to handle documents that may contain private information. The following practices should be followed:

- Never commit uploaded documents to GitHub.
- Keep `media/` in `.gitignore`.
- Never commit passwords or API keys.
- Keep `.env` files out of the repository.
- Do not commit databases containing real personal information.
- Use Django authentication and access controls.
- Validate uploaded files.
- Use HTTPS in production.
- Configure secure cookies in production.
- Restrict access to uploaded media.
- Use appropriate production database permissions.
- Avoid using real personal documents in development or public repositories.

## Development Database

SQLite is suitable for local development.

For production deployments, a database such as PostgreSQL can be considered.

## Production Considerations

For production, the application can be deployed using an architecture such as:

```text
Browser
  ↓
HTTPS
  ↓
Web Server
  ↓
Django
  ↓
PostgreSQL
  │
  └── Object/File Storage
```

Production configuration should include appropriate settings for:

- `DEBUG = False`
- `ALLOWED_HOSTS`
- Secret key management
- HTTPS
- Secure cookies
- Static files
- Media access
- Database credentials

## Future Improvements

Potential future features include:

- Advanced dashboard analytics
- PDF/Excel report generation
- Bulk document upload
- Document preview
- Document expiry tracking
- Email notifications
- Audit trail
- Advanced reporting
- Cloud file storage
- PostgreSQL production support

## Testing

Important areas to test include:

### Authentication
- Valid login
- Invalid login
- Logout
- Access control

### People
- Add person
- View profile
- Verify document completion

### Documents
- Upload document
- Search document
- Filter document
- Move document to Trash
- Restore document
- Permanently delete document

### Document Types
- Add type
- Edit type
- Activate/deactivate type
- Delete unused type

### Users
- Superuser creates normal user
- Normal user cannot manage project users

## Project Significance

DocManager demonstrates practical implementation of:

- Python programming
- Django framework
- MVT architecture
- CRUD operations
- Relational database design
- Django ORM
- Model relationships
- Authentication
- Authorization
- File upload
- File management
- Search and filtering
- Soft deletion
- Form handling
- Template rendering
- Static and media files
- Git/GitHub
- Role-based access control

## Screenshots

Add project screenshots here after preparing the public repository.

Example:

```text
docs/
├── dashboard.png
├── people.png
├── documents.png
├── document-types.png
└── settings.png
```

Then they can be displayed in this README using Markdown.

## Project Status

**Development Status:** Active Development

The core document-management workflow, authentication, people management, document management, document-type configuration, Trash/Restore functionality, and user management are implemented. Additional production-focused features can be added in future iterations.

## License

This project does not currently specify a license.

If you intend to allow others to use, modify, and distribute the project, consider adding an appropriate open-source license.

## Author

**Shahil**

Built as a Django-based document management project.
