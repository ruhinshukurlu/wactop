from django.db import models
from django.utils.translation import ugettext as _
from account.models import *
from slugify import slugify
from ckeditor.fields import RichTextField


class Organizer(models.Model):

    user = models.OneToOneField("account.User", verbose_name=_("User"), on_delete=models.CASCADE, related_name = 'organizer')
    email = models.EmailField(_("Email"), max_length=254, blank=True, null=True)
    organizer_name = models.CharField(max_length=127, unique=True)
    description = RichTextField(blank=True, null=True)

    website = models.URLField(max_length=255, blank=True, null=True)
    facebook = models.URLField(max_length=127, blank=True, null=True)
    instagram = models.URLField(max_length=127, blank=True, null=True)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    organizer_type = models.ForeignKey('OrganizerType', on_delete=models.SET_NULL, blank=True, null=True,related_name = 'organizer')
    about = RichTextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_number_1 = models.CharField(max_length=31, blank=True, null=True)
    contact_number_2 = models.CharField(max_length=31, blank=True, null=True)
    profile_photo = models.ImageField( upload_to='organizer/cover/', height_field=None, width_field=None, max_length=None)
    cover = models.ImageField(upload_to='organizer/cover/', height_field=None, width_field=None, max_length=None, blank=True, null=True)
    viewcount = models.IntegerField(default=0)

    slug = models.SlugField(_("Slug"), blank=True, null=True)

    def __str__ (self):
        return self.organizer_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.organizer_name)
        return super(Organizer, self).save(*args, **kwargs)



class OrganizerType(models.Model):
    type = models.CharField(max_length=31)
    def __str__ (self):
        return self.type

class OrganizerImage(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE,related_name = 'organizer_image')
    image = models.ImageField(upload_to='organizer/image/', height_field=None, width_field=None, max_length=None)
    def __str__ (self):
        return self.organizer.organizer_name


class OrganizerUrl(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE,related_name = 'organizer_url')
    url = models.URLField()
    def __str__ (self):
        return self.organizer.name


EPERIENCE_CHOICES = [
    ('1 year', '1 Year'),
    ('2 year', '2 Year'),
    ('3 year', '3 Year'),
    ('4 year', '4 Year'),
    ('5+ year', '5+ Year'),
]


class Guide(models.Model):

    organizer = models.ForeignKey(Organizer, verbose_name=_("Organizer"), on_delete=models.CASCADE, related_name = 'guide')
    name = models.CharField(_("Name"), max_length=50)
    surname = models.CharField(_("Surname"), max_length=50)
    experience =  models.CharField(_("Experience"), max_length=50, choices = EPERIENCE_CHOICES)
    certification = models.FileField(_("Certification"), upload_to='guide/certifications/')

    def __str__(self):
        return self.name


class Instructor(models.Model):

    organizer = models.ForeignKey(Organizer, verbose_name=_("Organizer"), on_delete=models.CASCADE, related_name = 'instructor')
    name = models.CharField(_("Name"), max_length=50)
    surname = models.CharField(_("Surname"), max_length=50)
    experience =  models.CharField(_("Experience"), max_length=50, choices = EPERIENCE_CHOICES)
    certification = models.FileField(_("Certification"), upload_to='instructor/certifications/')

    def __str__(self):
        return self.name


class Notification(models.Model):
    # informations
    user = models.ForeignKey("account.User", verbose_name=_("User"), on_delete=models.CASCADE, related_name = 'notification', blank=True, null=True)
    text = models.TextField(_("Text"), blank=True, null=True)

    # moderations
    is_published = models.BooleanField('is published', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text



class Contact(models.Model):

    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    email = models.EmailField(_("Email"), max_length=254)
    phone_number = models.CharField(_("Phone Number"), max_length=50)
    message = models.TextField(_("Message"))

    def __str__(self):
        return self.first_name
