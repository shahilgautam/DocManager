from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Person, DocumentType, Document

# User/superuser account management is intentionally kept out of the
# Django admin UI. Superuser account changes are terminal-only, and
# normal DocManager users are created from Settings inside the project.
for model in (User, Group):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    list_display = (
        "person_id",
        "name",
        "person_type",
        "department",
        "email",
        "created_at",
    )

    search_fields = (
        "person_id",
        "name",
        "email",
    )

    list_filter = (
        "person_type",
        "department",
    )


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "required_for",
        "allowed_file_types",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "required_for",
        "is_active",
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = (
        "person",
        "document_type",
        "status",
        "uploaded_at",
    )

    search_fields = (
        "person__name",
        "person__person_id",
        "document_type__name",
    )

    list_filter = (
        "status",
        "document_type",
        "uploaded_at",
    )
