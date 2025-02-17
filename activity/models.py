from django.db import models
from organizer.models import *
from tour.models import status_choices, Type, TourType
from multiselectfield import MultiSelectField
import smtplib
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from slugify import slugify
from Wactop.mail import *
from ckeditor.fields import RichTextField


class Activity(models.Model):

    CURRENCIES = [
        ('AZN', 'AZN'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('TRY', 'TRY'),
        ('RUB','RUB')
    ]

    organizer = models.ForeignKey(Organizer, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=63)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True, null=True)

    activity_type = models.ForeignKey(TourType, on_delete=models.CASCADE, related_name='activity')
    country = models.CharField(max_length=31, default='Azerbaijan')
    city = models.CharField(max_length=31, null=True, blank=True)
    address = models.CharField(max_length=63, null=True, blank=True)
    price = models.IntegerField()
    pricefor = models.IntegerField(default=1)
    currency = models.CharField(max_length=31, choices = CURRENCIES, default='AZN')
    discount = models.IntegerField(blank=True, null=True)
    distance = models.CharField(max_length=31, blank=True, null=True)
    durationday = models.IntegerField(blank=True, null=True)
    durationnight = models.IntegerField(blank=True, null=True)
    datefrom = models.DateField(blank=True, null=True)
    dateto = models.DateField(blank=True, null=True)
    viewcount = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='activity/avatar/', height_field=None, width_field=None, max_length=None, blank=True, null=True)
    cover = models.ImageField(upload_to='activity/cover/', height_field=None, width_field=None, max_length=None, blank=True, null=True)
    guide = models.CharField(max_length=31, blank=True, null=True)
    availabledays = models.CharField(max_length=31, blank=True, null=True)
    status = models.IntegerField(choices=status_choices, default=1)
    rating = models.IntegerField(_("Rating"), blank=True, null=True, default=0)

    map_link = models.URLField(_("Map Link"), max_length=300, blank=True, null=True)
    activated = models.BooleanField(_("Activated"), default  = False)

    slug = models.SlugField(_("Slug"), blank=True, null=True)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True )

    old_status = None
    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)
        self.old_status = self.status

    def get_duration_day(self):
        if self.datefrom and self.dateto:
            start_date = self.datefrom
            end_date = self.dateto
            return (end_date-start_date).days
        else:
            return False

    def discount_price(self):
        new_price = self.price - (self.price * self.discount) // 100
        return new_price

    def discount_price_api(self):
        if self.discount:
            new_price = self.price - (self.price * self.discount) // 100
        else:
            new_price = 0
        return new_price

    def get_duration_day_api(self):
        duration = ''
        if self.datefrom and self.dateto:
            start_date = self.datefrom
            end_date = self.dateto
            duration = f'{(end_date-start_date).days} days'
        else:
            duration = 'Always'

        return duration

    def __str__ (self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super(Activity, self).save(*args, **kwargs)

# class ActivityDetail(models.Model):
#     activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_detail')
#     title = models.CharField(max_length=31)
#     text = RichTextField()

#     def __str__ (self):
#         return self.activity.title + ": " + self.title


class ActivityImage(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='activity/image/', height_field=None, width_field=None, max_length=None)
    def __str__ (self):
        return self.activity.title

class ActivitySchedule(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    schedule_image = models.ImageField(upload_to='activity/schedule/', height_field=None, width_field=None, max_length=None)
    def __str__ (self):
        return self.activity.title

class ActivityUrl(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    url = models.URLField()
    def __str__ (self):
        return self.activity.title


class ActivityComment(models.Model):
    message = models.TextField(_("Text"))
    commented_at = models.DateField(_("Commented at"), auto_now_add=True)
    rating = models.IntegerField(_("Rating"), blank=True, null=True)

    comment_reply = models.ForeignKey("self", verbose_name=_("Comment"), on_delete=models.CASCADE, blank=True, null = True, related_name='replies')
    activity = models.ForeignKey("activity.Activity", verbose_name=_("Activity"), on_delete=models.CASCADE, blank=True, null=True, related_name='activity_comment')
    user = models.ForeignKey("account.User", verbose_name=_("User"), on_delete=models.CASCADE, blank=True, null=True, related_name='activity_comment')

    def __str__ (self):
        return self.message


class ActivityDeny(models.Model):
    # informations
    message = models.TextField(_("Text"))

    # relations
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='deny')

    # moderations
    created_at = models.DateField(_("Commented at"), auto_now_add=True)
    updated_at = models.DateField(_("Commented at"), auto_now=True)


    class Meta:
        verbose_name = _("ActivityDeny")
        verbose_name_plural = _("ActivityDenies")

    def __str__(self):
        return str(self.activity)