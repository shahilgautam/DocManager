from django import forms

from .models import Person, Document, DocumentType


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person

        fields = [
            "person_id",
            "name",
            "email",
            "phone",
            "person_type",
            "department",
        ]

        widgets = {
            "person_id": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Example: STU001 or EMP001",
            }),
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter full name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input",
                "placeholder": "Enter email address",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter phone number",
            }),
            "person_type": forms.Select(attrs={
                "class": "form-input",
            }),
            "department": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Example: Computer Science",
            }),
        }


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document

        fields = [
            "document_type",
            "file",
        ]

        widgets = {
            "document_type": forms.Select(attrs={
                "class": "form-input",
            }),
            "file": forms.ClearableFileInput(attrs={
                "class": "file-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["document_type"].queryset = (
            DocumentType.objects
            .filter(is_active=True)
            .order_by("name")
        )

    def clean_file(self):

        file = self.cleaned_data.get("file")

        if not file:
            raise forms.ValidationError(
                "Please select a file."
            )

        allowed_extensions = [
            ".pdf",
            ".txt",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".csv",
            ".jpg",
            ".jpeg",
            ".png",
        ]

        file_name = file.name.lower()

        if not any(
            file_name.endswith(ext)
            for ext in allowed_extensions
        ):
            raise forms.ValidationError(
                "This file type is not supported."
            )

        max_size = 10 * 1024 * 1024

        if file.size > max_size:
            raise forms.ValidationError(
                "File size must be less than 10 MB."
            )

        return file


class DocumentTypeForm(forms.ModelForm):

    class Meta:
        model = DocumentType

        fields = [
            "name",
            "description",
            "allowed_file_types",
            "required_for",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Example: Driving License",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-input description-input",
                "placeholder": "Describe this document type...",
                "rows": 4,
            }),
            "allowed_file_types": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Example: PDF, JPG, PNG",
            }),
            "required_for": forms.Select(attrs={
                "class": "form-input",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "checkbox-input",
            }),
        }


class UploadDocumentForm(forms.ModelForm):

    class Meta:
        model = Document

        fields = [
            "person",
            "document_type",
            "file",
        ]

        widgets = {
            "person": forms.Select(attrs={
                "class": "form-input",
            }),
            "document_type": forms.Select(attrs={
                "class": "form-input",
            }),
            "file": forms.ClearableFileInput(attrs={
                "class": "file-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["document_type"].queryset = (
            DocumentType.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields["person"].queryset = (
            Person.objects
            .all()
            .order_by("name")
        )

    def clean_file(self):

        file = self.cleaned_data.get("file")

        if not file:
            raise forms.ValidationError(
                "Please select a file."
            )

        allowed_extensions = [
            ".pdf",
            ".txt",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".csv",
            ".jpg",
            ".jpeg",
            ".png",
        ]

        file_name = file.name.lower()

        if not any(
            file_name.endswith(ext)
            for ext in allowed_extensions
        ):
            raise forms.ValidationError(
                "This file type is not supported."
            )

        max_size = 10 * 1024 * 1024

        if file.size > max_size:
            raise forms.ValidationError(
                "File size must be less than 10 MB."
            )

        return file


from django.contrib.auth.models import User


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter username",
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter first name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter last name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input",
                "placeholder": "Enter email address",
            }),
        }


class NormalUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Enter password",
        }),
        min_length=8,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Confirm password",
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter username",
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter first name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter last name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input",
                "placeholder": "Enter email address",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        if commit:
            user.save()
        return user
