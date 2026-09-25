import os

from django.db import models


class Person(models.Model):

    PERSON_TYPE_CHOICES = [
        ("student", "Student"),
        ("employee", "Employee"),
    ]

    person_id = models.CharField(
        max_length=30,
        unique=True
    )

    name = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    person_type = models.CharField(
        max_length=20,
        choices=PERSON_TYPE_CHOICES
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.name} ({self.person_id})"


class DocumentType(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    allowed_file_types = models.CharField(
        max_length=300,
        blank=True,
        help_text="Example: PDF, JPG, PNG"
    )

    required_for = models.CharField(
        max_length=20,
        choices=[
            ("student", "Student"),
            ("employee", "Employee"),
            ("both", "Both"),
        ],
        default="both"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Document(models.Model):

    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("rejected", "Rejected"),
    ]

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    file = models.FileField(
        upload_to="documents/%Y/%m/"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="submitted"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def file_name(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return f"{self.person.name} - {self.document_type.name}"