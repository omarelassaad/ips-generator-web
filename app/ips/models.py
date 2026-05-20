from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.is_approved else 'Not Approved'}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Ensure a profile is created if it doesn't exist for existing users
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class QuestionnaireResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=255, default="Unknown")  # Provide a default value
    answer = models.CharField(max_length=255, blank=True, null=True)  # Allowing null values
    score = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.question}"

class ChooseMyselfData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_owner = models.CharField(max_length=255)
    account_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    strategy = models.TextField()  # Changed from CharField to TextField
    version_number = models.CharField(max_length=50, default='N/A')

    def __str__(self):
        return f"{self.user.username} - {self.account_owner} - {self.account_type}"

class LetPmChooseData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_owner = models.CharField(max_length=255)
    account_type = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)
    additional_info = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['timestamp']


class ReturnsUpload(models.Model):
    file = models.FileField(upload_to='returns/', help_text="Excel file (.xlsx) with Sheet1 performance data")
    as_of_date = models.CharField(max_length=50, help_text='e.g. "March 31, 2026"')
    calendar_years = models.CharField(
        max_length=200,
        default='2025,2024,2023,2022,2021,2020,2019',
        help_text='Comma-separated list of calendar years to show in the performance table, most recent first.'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Only one upload should be active at a time. "
                  "Saving a new active upload automatically deactivates the previous one."
    )

    class Meta:
        verbose_name = "Returns Upload"
        verbose_name_plural = "Returns Uploads"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Returns as of {self.as_of_date} (uploaded {self.uploaded_at.strftime('%Y-%m-%d') if self.uploaded_at else '—'})"
