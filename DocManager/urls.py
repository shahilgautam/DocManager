
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
     
    path("", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("people/", views.people, name="people"),
    path("people/add/", views.add_person, name="add_person"),
    path("people/<int:person_id>/", views.person_profile, name="person_profile"),
    path("people/<int:person_id>/upload/", views.upload_document, name="upload_document"),
    path("documents/", views.all_documents, name="all_documents"),
    path("recent/", views.recent_documents, name="recent_documents"),
    path("document-types/", views.document_types, name="document_types"),
    path("document-types/add/", views.add_document_type, name="add_document_type"),
    path("document-types/<int:type_id>/edit/", views.edit_document_type, name="edit_document_type"),
    path("document-types/<int:type_id>/toggle/", views.toggle_document_type, name="toggle_document_type"),
    path("document-types/<int:type_id>/delete/", views.delete_document_type, name="delete_document_type"),
    path("documents/upload/", views.upload_document_general, name="upload_document_general"),
    path("trash/", views.trash, name="trash"),
    path("documents/<int:document_id>/trash/", views.move_to_trash, name="move_to_trash"),
    path("documents/<int:document_id>/restore/", views.restore_document, name="restore_document"),
    path("documents/<int:document_id>/permanent-delete/", views.permanent_delete_document, name="permanent_delete_document"),
    path("settings/", views.settings, name="settings"),
    path("settings/profile/", views.edit_profile, name="edit_profile"),
    path("settings/password/", views.change_password, name="change_password"),
    path("settings/users/", views.project_users, name="project_users"),
    path("settings/users/add/", views.add_project_user, name="add_project_user"),
    path("settings/users/<int:user_id>/toggle/", views.toggle_project_user, name="toggle_project_user"),
    path("settings/users/<int:user_id>/delete/", views.delete_project_user, name="delete_project_user"),
]
