from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django_extensions.db.fields import ShortUUIDField
import shortuuid
import jsonfield
class User(AbstractUser):
    is_organisor = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class JobManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

def get_uuid():
    return shortuuid.uuid()

class Job(models.Model):
    CHANNELS = [("WhatsApp","WhatsApp"),
                ("Facebook Messenger", "Facebook Messenger"),
                ("Telegram","Telegram"),
                ("Web","Web") ]
    PAYMENT_STATUS = [("Unpaid", "Unpaid"),
                      ("Paid", "Paid")]
    STATUS = [("Closed", "Closed"),
              ("Open", "Open"),
              ("In_Progress", "In_Progress")]
    SESSION_STATUS = [("Active", "Active"),("Inactive", "Inactive")]
    uuid = ShortUUIDField(default=get_uuid,unique=True)
    channel = models.CharField(choices=CHANNELS,max_length=20)
    channel_id = models.CharField(max_length=255)
    session_status = models.CharField(choices=SESSION_STATUS,max_length=20)
    year_of_filling = models.IntegerField(null=True)
    full_name = models.CharField(max_length=20,null=True)
    kra_pin = models.CharField(max_length=20,null=True)
    kra_password = models.CharField(max_length=20,null=True)
    nhif_no = models.CharField(max_length=20,null=True)
    file_nil = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20,null=True)
    expected_payment_amount = models.IntegerField(default=1)
    output_option = models.CharField(max_length=10,null=True)
    mpesa_paid_amount = models.IntegerField(default=0)
    mpesa_reference = models.CharField(max_length=20,null=True)
    screenshot_path = models.CharField(max_length=500,null=True)
    payment_status = models.CharField(choices=PAYMENT_STATUS,max_length=20,default="Unpaid")
    status = models.CharField(choices=STATUS,max_length=20,default="In_Progress")
    step = models.CharField(max_length=50,default="START")
    tax_document_extracted_info = jsonfield.JSONField(default=list)
    #organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent = models.ForeignKey("Agent", null=True, blank=True, on_delete=models.SET_NULL)
    #category = models.ForeignKey("Category", related_name="jobs", null=True, blank=True, on_delete=models.SET_NULL)
    date_added = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null=True, blank=True)
    objects = JobManager()

    def __str__(self):
        return f"{self.uuid}"


def handle_upload_follow_ups(instance, filename):
    return f"lead_followups/lead_{instance.job.pk}/{filename}"


class FollowUp(models.Model):
    job = models.ForeignKey(Job, related_name="followups", on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    file = models.FileField(null=True, blank=True, upload_to=handle_upload_follow_ups)

    def __str__(self):
        return f"{self.job.first_name} {self.job.last_name}"


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email


class Category(models.Model):
    name = models.CharField(max_length=30)  # New, Contacted, Converted, Unconverted
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(post_user_created_signal, sender=User)