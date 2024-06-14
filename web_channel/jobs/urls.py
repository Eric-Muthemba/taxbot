
from django.urls import path
from .views import (
    LeadListView, LeadDetailView, LeadCreateView, LeadUpdateView, LeadDeleteView,
    AssignAgentView, CategoryListView, CategoryDetailView, LeadCategoryUpdateView,
    CategoryCreateView, CategoryUpdateView, CategoryDeleteView, LeadJsonView, MpesaCallback,
    FollowUpCreateView, FollowUpUpdateView, FollowUpDeleteView
)

app_name = "jobs"

urlpatterns = [
    path('', LeadListView.as_view(), name='job-list'),
    path('json/', LeadJsonView.as_view(), name='job-list-json'),
    path('<int:pk>/', LeadDetailView.as_view(), name='job-detail'),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name='job-update'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='job-delete'),
    path('<int:pk>/assign-agent/', AssignAgentView.as_view(), name='assign-agent'),
    path('<int:pk>/category/', LeadCategoryUpdateView.as_view(), name='job-category-update'),
    path('<int:pk>/followups/create/', FollowUpCreateView.as_view(), name='job-followup-create'),
    path('followups/<int:pk>/', FollowUpUpdateView.as_view(), name='job-followup-update'),
    path('followups/<int:pk>/delete/', FollowUpDeleteView.as_view(), name='job-followup-delete'),
    path('create/', LeadCreateView.as_view(), name='job-create'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('create-category/', CategoryCreateView.as_view(), name='category-create'),
    path('qwertyuiop/mpesa_callback', MpesaCallback.as_view(), name='mpesa'),

]