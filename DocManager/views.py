from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db import models

from .models import Person, DocumentType, Document
from .forms import (
    PersonForm, DocumentForm, DocumentTypeForm, UploadDocumentForm,
    UserProfileForm, NormalUserCreationForm,
)
from django.utils import timezone

@login_required
@permission_required("DocManager.view_person", raise_exception=True)
@permission_required("DocManager.view_document", raise_exception=True)
@permission_required("DocManager.view_documenttype", raise_exception=True)
def dashboard(request):
    # People statistics
    total_people = Person.objects.count()
    total_students = Person.objects.filter(person_type="student").count()
    total_employees = Person.objects.filter(person_type="employee").count()

    # Active documents only; documents in Trash are excluded from dashboard totals.
    active_documents = Document.objects.filter(is_deleted=False)
    total_files = active_documents.count()
    submitted_files = active_documents.filter(status="submitted").count()
    rejected_files = active_documents.filter(status="rejected").count()

    # Calculate required document slots across all people.
    # A submitted document satisfies one required document type for that person.
    required_slots = 0
    submitted_required_documents = 0

    for person in Person.objects.all().only("id", "person_type"):
        required_types = DocumentType.objects.filter(
            required_for__in=[person.person_type, "both"],
            is_active=True
        )
        required_count = required_types.count()
        submitted_count = person.documents.filter(
            document_type__in=required_types,
            is_deleted=False
        ).values("document_type_id").distinct().count()

        required_slots += required_count
        submitted_required_documents += min(submitted_count, required_count)

    missing_documents = max(required_slots - submitted_required_documents, 0)
    completion_percentage = 0
    if required_slots > 0:
        completion_percentage = round(
            (submitted_required_documents / required_slots) * 100,
            1
        )

    # File-type distribution for active uploaded files.
    file_type_definitions = [
        ("PDF", "bi-file-earmark-pdf", [".pdf"]),
        ("Images", "bi-image", [".jpg", ".jpeg", ".png", ".gif", ".webp"]),
        ("Excel", "bi-file-earmark-spreadsheet", [".xls", ".xlsx", ".csv"]),
        ("Word", "bi-file-earmark-word", [".doc", ".docx"]),
        ("Text", "bi-file-earmark-text", [".txt"]),
    ]

    file_type_counts = []
    for label, icon, extensions in file_type_definitions:
        count = 0
        for document in active_documents.only("file"):
            name = document.file.name.lower()
            if any(name.endswith(extension) for extension in extensions):
                count += 1
        file_type_counts.append({
            "label": label,
            "icon": icon,
            "count": count,
            "percentage": round((count / total_files) * 100, 1) if total_files else 0,
        })

    recent_uploads = active_documents.select_related(
        "person", "document_type"
    ).order_by("-uploaded_at")[:5]

    context = {
        "total_people": total_people,
        "total_students": total_students,
        "total_employees": total_employees,
        "total_files": total_files,
        "submitted_files": submitted_files,
        "rejected_files": rejected_files,
        "missing_documents": missing_documents,
        "completion_percentage": completion_percentage,
        "file_type_counts": file_type_counts,
        "recent_uploads": recent_uploads,
    }

    return render(request, "dashboard.html", context)


@login_required
@permission_required("DocManager.view_person", raise_exception=True)
def people(request):

    people = Person.objects.all().order_by("-created_at")

    for person in people:

        required_documents = DocumentType.objects.filter(
            required_for__in=[
                person.person_type,
                "both"
            ],
            is_active=True
        )

        total_documents = required_documents.count()

        submitted_count = person.documents.filter(
            document_type__in=required_documents,
            is_deleted=False
        ).values(
            "document_type"
        ).distinct().count()

        person.total_documents = total_documents
        person.submitted_count = submitted_count
        person.missing_count = total_documents - submitted_count

        if total_documents > 0:
            person.completion_percentage = round(
                (submitted_count / total_documents) * 100
            )
        else:
            person.completion_percentage = 0

    return render(
        request,
        "people.html",
        {
            "people": people
        }
    )


@login_required
@permission_required("DocManager.view_person", raise_exception=True)
@permission_required("DocManager.view_document", raise_exception=True)
@permission_required("DocManager.view_documenttype", raise_exception=True)
def person_profile(request, person_id):

    person = get_object_or_404(
        Person,
        id=person_id
    )

    document_types = DocumentType.objects.filter(
        is_active=True
    )

    submitted_documents = person.documents.select_related(
    "document_type"
        ).filter(
        is_deleted=False
    )

    submitted_type_ids = submitted_documents.values_list(
        "document_type_id",
        flat=True
    )

    required_documents = document_types.filter(
        required_for__in=[
            person.person_type,
            "both"
        ]
    )

    total_documents = required_documents.count()

    submitted_count = required_documents.filter(
        id__in=submitted_type_ids
    ).count()

    missing_count = total_documents - submitted_count

    completion_percentage = 0

    if total_documents > 0:
        completion_percentage = round(
            (submitted_count / total_documents) * 100
        )

    return render(
        request,
        "person_profile.html",
        {
            "person": person,
            "required_documents": required_documents,
            "submitted_documents": submitted_documents,
            "submitted_type_ids": submitted_type_ids,
            "total_documents": total_documents,
            "submitted_count": submitted_count,
            "missing_count": missing_count,
            "completion_percentage": completion_percentage,
        }
    )

@login_required
@permission_required("DocManager.add_person", raise_exception=True)
def add_person(request):

    if request.method == "POST":

        form = PersonForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("people")

    else:

        form = PersonForm()

    return render(
        request,
        "add_person.html",
        {
            "form": form
        }
    )

@login_required
@permission_required("DocManager.add_document", raise_exception=True)
def upload_document(request, person_id):

    person = get_object_or_404(
        Person,
        id=person_id
    )

    selected_type = request.GET.get(
        "document_type"
    )

    if request.method == "POST":

        form = DocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            document = form.save(
                commit=False
            )

            document.person = person

            document.save()

            return redirect(
                "person_profile",
                person_id=person.id
            )

    else:

        if selected_type:

            form = DocumentForm(
                initial={
                    "document_type": selected_type
                }
            )

        else:

            form = DocumentForm()

    return render(
        request,
        "upload_document.html",
        {
            "person": person,
            "form": form,
        }
    )

@login_required
@permission_required("DocManager.view_document", raise_exception=True)
def all_documents(request):

    documents = Document.objects.select_related(
        "person",
        "document_type"
    ).filter(
        is_deleted=False
    ).order_by("-uploaded_at")

    search = request.GET.get(
        "search",
        ""
    ).strip()

    document_type = request.GET.get(
        "document_type",
        ""
    )

    try:
        document_type = int(document_type)
    except (ValueError, TypeError):
        document_type = None

    person_type = request.GET.get(
        "person_type",
        ""
    )

    status = request.GET.get(
        "status",
        ""
    )

    # SEARCH

    if search:

        documents = documents.filter(

            models.Q(
                file__icontains=search
            )

            |

            models.Q(
                person__name__icontains=search
            )

            |

            models.Q(
                person__person_id__icontains=search
            )

            |

            models.Q(
                document_type__name__icontains=search
            )
        )

    # DOCUMENT TYPE FILTER

    if document_type:

        documents = documents.filter(
            document_type_id=document_type
        )

    # PERSON TYPE FILTER

    if person_type:

        documents = documents.filter(
            person__person_type=person_type
        )

    # STATUS FILTER

    if status:

        documents = documents.filter(
            status=status
        )

    # ACTIVE DOCUMENT TYPES

    document_types = DocumentType.objects.filter(
        is_active=True
    ).order_by("name")
    for doc_type in document_types:
        doc_type.active_document_count = Document.objects.filter(
            document_type=doc_type,
            is_deleted=False
        ).count()

    # PEOPLE

    people = Person.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "all_documents.html",
        {
            "documents": documents,
            "document_types": document_types,
            "people": people,
            "search": search,
            "selected_document_type": document_type,
            "selected_person_type": person_type,
            "selected_status": status,
        }
    )
@login_required
@permission_required("DocManager.view_document", raise_exception=True)
def recent_documents(request):
    documents = Document.objects.select_related(
        "person",
        "document_type"
    ).filter(
        is_deleted=False
    ).order_by("-uploaded_at")[:20]

    return render(request, "recent_documents.html", {
        "documents": documents,
    })
    
@login_required
@permission_required("DocManager.view_documenttype", raise_exception=True)
def document_types(request):

    document_types = DocumentType.objects.all().order_by("name")

    active_count = document_types.filter(
        is_active=True
    ).count()

    student_count = document_types.filter(
        required_for__in=["student", "both"]
    ).count()

    employee_count = document_types.filter(
        required_for__in=["employee", "both"]
    ).count()

    return render(
        request,
        "document_types.html",
        {
            "document_types": document_types,
            "active_count": active_count,
            "student_count": student_count,
            "employee_count": employee_count,
        }
    )

@login_required
@permission_required("DocManager.add_documenttype", raise_exception=True)
def add_document_type(request):

    if request.method == "POST":

        form = DocumentTypeForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("document_types")

    else:

        form = DocumentTypeForm()

    return render(
        request,
        "add_document_type.html",
        {
            "form": form
        }
    )

@login_required
@permission_required("DocManager.change_documenttype", raise_exception=True)
def edit_document_type(request, type_id):

    document_type = get_object_or_404(
        DocumentType,
        id=type_id
    )

    if request.method == "POST":

        form = DocumentTypeForm(
            request.POST,
            instance=document_type
        )

        if form.is_valid():

            form.save()

            return redirect("document_types")

    else:

        form = DocumentTypeForm(
            instance=document_type
        )

    return render(
        request,
        "edit_document_type.html",
        {
            "form": form,
            "document_type": document_type,
        }
    )

@login_required
@permission_required("DocManager.change_documenttype", raise_exception=True)
def toggle_document_type(request, type_id):

    document_type = get_object_or_404(
        DocumentType,
        id=type_id
    )

    document_type.is_active = not document_type.is_active

    document_type.save(
        update_fields=["is_active"]
    )

    return redirect("document_types")

@login_required
@permission_required("DocManager.delete_documenttype", raise_exception=True)
def delete_document_type(request, type_id):

    document_type = get_object_or_404(
        DocumentType,
        id=type_id
    )

    if request.method == "POST":

        if document_type.documents.exists():

            return render(
                request,
                "delete_document_type.html",
                {
                    "document_type": document_type,
                    "cannot_delete": True,
                    "document_count":
                        document_type.documents.count(),
                }
            )

        document_type.delete()

        return redirect("document_types")

    return render(
        request,
        "delete_document_type.html",
        {
            "document_type": document_type,
            "cannot_delete": False,
        }
    )    

@login_required
@permission_required("DocManager.add_document", raise_exception=True)
def upload_document_general(request):

    if request.method == "POST":

        form = UploadDocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            return redirect("all_documents")

    else:

        form = UploadDocumentForm()

    return render(
        request,
        "upload_document_general.html",
        {
            "form": form
        }
    )

@login_required
@permission_required("DocManager.view_document", raise_exception=True)
def trash(request):
    documents = Document.objects.select_related(
        "person",
        "document_type"
    ).filter(
        is_deleted=True
    ).order_by("-deleted_at")

    return render(request, "trash.html", {
        "documents": documents,
    })

@login_required
@permission_required("DocManager.change_document", raise_exception=True)
def move_to_trash(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if request.method == "POST":
        document.is_deleted = True
        document.deleted_at = timezone.now()
        document.save(update_fields=["is_deleted", "deleted_at"])

    return redirect("all_documents")

@login_required
@permission_required("DocManager.change_document", raise_exception=True)
def restore_document(request, document_id):
    document = get_object_or_404(
        Document,
        id=document_id,
        is_deleted=True
    )

    if request.method == "POST":
        document.is_deleted = False
        document.deleted_at = None
        document.save(update_fields=["is_deleted", "deleted_at"])

    return redirect("trash")

@login_required
@permission_required("DocManager.delete_document", raise_exception=True)
def permanent_delete_document(request, document_id):
    document = get_object_or_404(
        Document,
        id=document_id,
        is_deleted=True
    )

    if request.method == "POST":
        if document.file:
            document.file.delete(save=False)

        document.delete()

    return redirect("trash")

@login_required
def settings(request):
    user = request.user
    if user.is_superuser:
        role = "Superuser"
    elif user.is_staff:
        role = "User"
    else:
        role = "User"

    return render(
        request,
        "settings.html",
        {
            "profile_user": user,
            "role": role,
        }
    )


@login_required
def edit_profile(request):
    if request.user.is_superuser:
        messages.info(request, "Superuser profile changes are managed from the terminal.")
        return redirect("settings")
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("settings")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.user.is_superuser:
        messages.info(request, "Superuser password changes are managed from the terminal.")
        return redirect("settings")
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        for field in form.fields.values():
            field.widget.attrs["class"] = "form-input"
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("settings")
    else:
        form = PasswordChangeForm(request.user)
        for field in form.fields.values():
            field.widget.attrs["class"] = "form-input"

    return render(request, "change_password.html", {"form": form})

def superuser_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Only the system superuser can manage DocManager users.")
            return redirect("settings")
        return view_func(request, *args, **kwargs)
    return wrapper


@superuser_required
def project_users(request):
    users = User.objects.filter(is_superuser=False).order_by("username")
    return render(request, "project_users.html", {"users": users})


@superuser_required
def add_project_user(request):
    if request.method == "POST":
        form = NormalUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            permissions = Permission.objects.filter(content_type__app_label="DocManager")
            user.user_permissions.set(permissions)
            messages.success(request, f"User '{user.username}' was created with Full Access.")
            return redirect("project_users")
    else:
        form = NormalUserCreationForm()
    return render(request, "add_project_user.html", {"form": form})


@superuser_required
def toggle_project_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    if request.method == "POST":
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.success(request, f"{user.username} has been {'activated' if user.is_active else 'deactivated'}.")
    return redirect("project_users")


@superuser_required
def delete_project_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' was deleted.")
    return redirect("project_users")
