import json
import logging
import datetime
from django import contrib
from django.contrib import messages
from django.core.mail import send_mail
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import generic
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Job, Agent, Category, FollowUp
from .forms import (
    LeadForm, 
    LeadModelForm, 
    CustomUserCreationForm, 
    AssignAgentForm, 
    LeadCategoryUpdateForm,
    CategoryModelForm,
    FollowUpModelForm
)
from rest_framework import generics
from django.http import HttpResponse,JsonResponse
from .serializers import ConversationSerializer
import uuid
from rest_framework.parsers import MultiPartParser, FormParser
from app.celery import app
from django.conf import settings
import os
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db.models import Q  # For advanced filtering
from .utilities import state_machine
logger = logging.getLogger(__name__)


# CRUD+L - Create, Retrieve, Update and Delete + List

def landing_page(request):
    return render(request, "landing.html")

def landing_page(request):
    return render(request, "landing.html")

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")

class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

class DashboardView(OrganisorAndLoginRequiredMixin, generic.TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        user = self.request.user

        # How many jobs we have in total
        total_lead_count = Job.objects.all().count()

        # How many new jobs in the last 30 days
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

        total_in_past30 = Job.objects.filter(date_added__gte=thirty_days_ago).count()

        # How many converted jobs in the last 30 days
        converted_category = Category.objects.filter(name="Converted")
        query = {"close_date__gte":thirty_days_ago}
        if converted_category.count() >0:
            query["category"] = 0
        converted_in_past30 = Job.objects.filter(**query).count()

        context.update({
            "total_lead_count": total_lead_count,
            "total_in_past30": total_in_past30,
            "converted_in_past30": converted_in_past30
        })
        return context


class Chatbot2PageView(generic.TemplateView):
    template_name = "chatbot2.html"

    def dispatch(self, request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)

class ChatbotTermsAndConditionsView(generic.TemplateView):
    template_name = "terms_and_conditions.html"

    def dispatch(self, request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)

class MpesaCallback(generics.CreateAPIView):
    serializer_class = ConversationSerializer
    def create(self, request, *args, **kwargs):
        data = request.data
        print(data)

        if data["Body"]["stkCallback"]["ResultCode"] == 0:
            reference = data["Body"]["stkCallback"]["ExternalReference"]
            amount_paid = data["Body"]["stkCallback"]["Amount"]
            mpesa_reference = [data_point["Value"] for data_point in data["Body"]["stkCallback"]["CallbackMetadata"]["Item"] if data_point["Name"]== "MpesaReceiptNumber"][0]
            jobs = Job.objects.filter(uuid=reference)
            jobs.update(mpesa_paid_amount=amount_paid,mpesa_reference=mpesa_reference)

        return JsonResponse({})


class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "jobs/lead_list.html"
    context_object_name = "jobs"

    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.all() if user.is_organisor else Job.objects.filter(organisation=user.agent.organisation,
                                                                                  agent__isnull=False, agent__user=user)


        filter_params = self.request.GET.dict()

        query = Q()
        for field, value in filter_params.items():
            if value != "":
                if field  == "payment_status":
                    query &= Q(**{field: value})
                else:
                    query &= Q(**{f"{field}__icontains": value})

        print(query)
        queryset = queryset.filter(query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organisor:
            context.update({"unassigned_leads": Job.objects.all()})

        '''
        # Add filter parameters to the context
        context['filter_params'] = self.request.GET.dict()
        # Add pagination information to the context
        # Add pagination information to the context
        jobs = context['jobs']
        

        paginator = Paginator(jobs, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        print(dir(page_obj))
        print(page_obj.count)

        '''


        '''context['page_obj'] = page_obj
        context['has_next'] = page_obj.has_next()
        context['has_previous'] = page_obj.has_previous()
        context['page_range'] = paginator.page_range

        #page_obj = context.get('page_obj')
        if page_obj:
            context['has_next'] = page_obj.has_next()
            context['has_previous'] = page_obj.has_previous()
            context['page_range'] = page_obj.paginator.page_range'''

        return context




class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "jobs/lead_detail.html"
    context_object_name = "job"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        if user.is_organisor:
            queryset = Job.objects.filter(organisation=user.userprofile)
        else:
            queryset = Job.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset


def lead_detail(request, pk):
    job = Job.objects.get(id=pk)
    context = {
        "job": job
    }
    return render(request, "jobs/lead_detail.html", context)


class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "jobs/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("jobs:job-list")

    def form_valid(self, form):
        job = form.save(commit=False)
        job.organisation = self.request.user.userprofile
        job.save()
        send_mail(
            subject="A job has been created",
            message="Go to the site to see the new job",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        messages.success(self.request, "You have successfully created a job")
        return super(LeadCreateView, self).form_valid(form)


def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/jobs")
    context = {
        "form": form
    }
    return render(request, "jobs/lead_create.html", context)


class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "jobs/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        return Job.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse("jobs:job-list")

    def form_valid(self, form):
        form.save()
        messages.info(self.request, "You have successfully updated this job")
        return super(LeadUpdateView, self).form_valid(form)


def lead_update(request, pk):
    job = Job.objects.get(id=pk)
    form = LeadModelForm(instance=job)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect("/jobs")
    context = {
        "form": form,
        "job": job
    }
    return render(request, "jobs/lead_update.html", context)


class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "jobs/lead_delete.html"

    def get_success_url(self):
        return reverse("jobs:job-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        return Job.objects.filter(organisation=user.userprofile)


def lead_delete(request, pk):
    job = Job.objects.get(id=pk)
    job.delete()
    return redirect("/jobs")


class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "jobs/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs
        
    def get_success_url(self):
        return reverse("jobs:job-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        job = Job.objects.get(id=self.kwargs["pk"])
        job.agent = agent
        job.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "jobs/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset = Job.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Job.objects.filter(
                organisation=user.agent.organisation
            )

        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "jobs/category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class CategoryCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "jobs/category_create.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("jobs:category-list")

    def form_valid(self, form):
        category = form.save(commit=False)
        category.organisation = self.request.user.userprofile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)


class CategoryUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "jobs/category_update.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("jobs:category-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class CategoryDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "jobs/category_delete.html"

    def get_success_url(self):
        return reverse("jobs:category-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "jobs/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        if user.is_organisor:
            queryset = Job.objects.filter(organisation=user.userprofile)
        else:
            queryset = Job.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("jobs:job-detail", kwargs={"pk": self.get_object().id})

    def form_valid(self, form):
        lead_before_update = self.get_object()
        instance = form.save(commit=False)
        converted_category = Category.objects.get(name="Converted")
        if form.cleaned_data["category"] == converted_category:
            # update the date at which this job was converted
            if lead_before_update.category != converted_category:
                # this job has now been converted
                instance.converted_date = datetime.datetime.now()
        instance.save()
        return super(LeadCategoryUpdateView, self).form_valid(form)


class FollowUpCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "jobs/followup_create.html"
    form_class = FollowUpModelForm

    def get_success_url(self):
        return reverse("jobs:job-detail", kwargs={"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super(FollowUpCreateView, self).get_context_data(**kwargs)
        context.update({
            "job": Job.objects.get(pk=self.kwargs["pk"])
        })
        return context

    def form_valid(self, form):
        job = Job.objects.get(pk=self.kwargs["pk"])
        followup = form.save(commit=False)
        followup.job = job
        followup.save()
        return super(FollowUpCreateView, self).form_valid(form)


class FollowUpUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "jobs/followup_update.html"
    form_class = FollowUpModelForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        if user.is_organisor:
            queryset = FollowUp.objects.filter(lead__organisation=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(lead__organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(lead__agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("jobs:job-detail", kwargs={"pk": self.get_object().job.id})


class FollowUpDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "jobs/followup_delete.html"

    def get_success_url(self):
        followup = FollowUp.objects.get(id=self.kwargs["pk"])
        return reverse("jobs:job-detail", kwargs={"pk": followup.job.pk})

    def get_queryset(self):
        user = self.request.user
        # initial queryset of jobs for the entire organisation
        if user.is_organisor:
            queryset = FollowUp.objects.filter(lead__organisation=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(lead__organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(lead__agent__user=user)
        return queryset



# def lead_update(request, pk):
#     job = Job.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == "POST":
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             job.first_name = first_name
#             job.last_name = last_name
#             job.age = age
#             job.save()
#             return redirect("/jobs")
    # context = {
    #     "form": form,
    #     "job": job
    # }
#     return render(request, "jobs/lead_update.html", context)


# def lead_create(request):
    # form = LeadForm()
    # if request.method == "POST":
    #     form = LeadForm(request.POST)
    #     if form.is_valid():
    #         first_name = form.cleaned_data['first_name']
    #         last_name = form.cleaned_data['last_name']
    #         age = form.cleaned_data['age']
    #         agent = Agent.objects.first()
    #         Job.objects.create(
    #             first_name=first_name,
    #             last_name=last_name,
    #             age=age,
    #             agent=agent
    #         )
    #         return redirect("/jobs")
    # context = {
    #     "form": form
    # }
#     return render(request, "jobs/lead_create.html", context)


class LeadJsonView(generic.View):

    def get(self, request, *args, **kwargs):
        
        qs = list(Job.objects.all().values(
            "first_name", 
            "last_name", 
            "age")
        )

        return JsonResponse({
            "qs": qs,
        })