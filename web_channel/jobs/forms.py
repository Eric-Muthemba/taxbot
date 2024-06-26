from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from .models import Job, Agent, Category, FollowUp

User = get_user_model()


class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = (
            'full_name',
            'channel_id',
            'kra_pin',
            'agent',
            'payment_status',
            'channel',
        )




    def clean_first_name(self):
        data = self.cleaned_data["full_name"]
        # if data != "Joe":
        #     raise ValidationError("Your name is not Joe")
        return data

    def clean(self):
        pass
        # first_name = self.cleaned_data["first_name"]
        # last_name = self.cleaned_data["last_name"]
        # if first_name + last_name != "Joe Soap":
        #     raise ValidationError("Your name is not Joe Soap")



class LeadForm(forms.Form):
    full_name = forms.CharField()



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}


class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        agents = Agent.objects.filter(organisation=request.user.userprofile)
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents


class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = (
            'channel_id',
        )


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            'name',
        )


class FollowUpModelForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = (
            'notes',
            'file'
        )