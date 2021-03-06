from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save
from django.http import request
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver


class Country(models.Model):
    """All countries Data"""
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Organisation(models.Model):
    """Property Management Companies or Estate Agents"""
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    email = models.EmailField
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class UserManager(BaseUserManager):
    """Helps Django work with our custom user model"""

    def create_user(self, email, password=None):
        """Creates a new user """

        if not email:
            raise ValueError('User must have an email address.')

        email = self.normalize_email(email)
        user = self.model(email=email)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser with given details."""

        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
        Represents a "user" inside our system. Stores all user account related data
    """
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    # REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        """Django uses this when it needs to get the user's full name."""

        return self.first_name + self.last_name

    def get_short_name(self):
        """Django uses this when it needs to get the users abbreviated name."""

        return self.first_name

    def __str__(self):
        """Django uses this when it needs to convert the object to text."""

        return self.email


class PropertyManager(models.Model):
    """Property Manager who will be using the platform"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.user.email


class LandLord(models.Model):
    """Property Owners"""
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='country')
    identification_type = models.CharField(max_length=55, choices=settings.ID_TYPES)
    identification = models.CharField(max_length=255)
    nationality = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='nationality')
    bank = models.CharField(max_length=255)
    bank_branch = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    representative = models.CharField(max_length=255, blank=True)
    managed_by = models.ForeignKey('Organisation', on_delete=models.CASCADE, default=2)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('manager:landlord_detail', kwargs={'pk': self.pk})


class Property(models.Model):
    """Property Instance, can be a building, land, land and building"""
    property_type = models.CharField(max_length=55, choices=settings.PROPERTY_TYPES)
    organisation_managing = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    land_lord = models.ForeignKey('LandLord', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    property_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    description = models.TextField()
    lot_size = models.DecimalField(max_digits=15, decimal_places=3, default=0.000)
    building_size = models.DecimalField(max_digits=15, decimal_places=3, default=0.000)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    geographic_location = models.CharField(max_length=255, blank=True, null=True)
    first_erected_date = models.DateField(blank=True, null=True)
    property_acquired_date = models.DateField(blank=True, null=True)
    acquisition_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    management_started_date = models.DateField(blank=True, null=True)
    management_stopped_date = models.DateField(blank=True, null=True)
    property_disposed_date = models.DateField(blank=True, null=True)
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    zone = models.CharField(max_length=255, blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('manager:property_detail', kwargs={'pk': self.pk})


class PropertyUnit(models.Model):
    """Parking Units, Clustered Property Single Rentable Units"""
    property = models.ForeignKey('Property', on_delete=models.CASCADE)
    unit_title = models.CharField(max_length=255)
    total_area = models.DecimalField(max_digits=15, decimal_places=3, default=0.000)
    is_vacant = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.unit_title

    def get_absolute_url(self):
        return reverse_lazy('manager:property_units_detail', kwargs={'pk': self.pk, 'prop': self.property_id})


class Premise(models.Model):
    """Single Apartments in an Apartment building or Floors in an office building: single rentable entities"""
    property = models.ForeignKey('Property', on_delete=models.CASCADE)
    premise_title = models.CharField(max_length=255)
    accommodation_type = models.CharField(choices=settings.ACCOMMODATION_TYPES, max_length=55)
    total_area = models.DecimalField(max_digits=15, decimal_places=3, default=0.000)
    is_vacant = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.premise_title

    def get_absolute_url(self):
        return reverse_lazy('manager:property_premises_detail', kwargs={'pk': self.pk, 'prop': self.property_id})


class Tenant(models.Model):
    tenant_name = models.CharField(max_length=255)
    trading_as_list_name = models.CharField(max_length=255)
    property = models.ForeignKey('Property', on_delete=models.CASCADE)
    identification_type = models.CharField(max_length=55, choices=settings.ID_TYPES)
    identification = models.CharField(max_length=255)
    email_1 = models.EmailField()
    email_2 = models.EmailField(blank=True, null=True)
    phone_1 = models.CharField(max_length=20)
    phone_2 = models.CharField(max_length=20, blank=True, null=True)
    postal_address = models.TextField()
    domicile_address = models.TextField(blank=True, null=True)
    nationality = models.ForeignKey('Country', on_delete=models.CASCADE)
    details = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    lease = models.OneToOneField('Lease', on_delete=models.CASCADE, related_name=_('lease'), blank=True, null=True)

    def __str__(self):
        return self.tenant_name

    def get_absolute_url(self):
        return reverse_lazy('manager:property_tenant_detail', kwargs={'pk': self.pk, 'prop': self.property_id})


class Lease(models.Model):
    tenant_lessee = models.OneToOneField('Tenant', on_delete=models.CASCADE, related_name=_('tenant'))
    tenant_representative = models.CharField(max_length=255, blank=True, null=True)
    tenant_representative_capacity = models.CharField(max_length=255, blank=True, null=True)
    owner_lessor = models.ForeignKey('LandLord', on_delete=models.CASCADE)
    owner_representative = models.CharField(max_length=255, blank=True, null=True)
    owner_representative_capacity = models.CharField(max_length=255, blank=True, null=True)
    organization_managing = models.ForeignKey('Organisation', on_delete=models.CASCADE)
    created_by_manager = models.ForeignKey('PropertyManager', on_delete=models.DO_NOTHING)
    premises = models.OneToOneField('Premise', on_delete=models.CASCADE, blank=True, null=True)
    property_unit = models.OneToOneField('PropertyUnit', on_delete=models.CASCADE, blank=True, null=True)
    entire_property = models.BooleanField(default=False)
    lease_starts = models.DateField()
    occupation_date = models.DateField()
    lease_ends = models.DateField(blank=True, null=True)
    lease_indefinite_thereafter = models.BooleanField(default=False)
    rent_review_date = models.DateField()
    annual_rent_review_date = models.DateField()
    rent_review_notes = models.TextField(blank=True, null=True)
    monthly_rent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    monthly_rate = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    escalation_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    recovery_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    monthly_recovery_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    recovery_notes = models.TextField(blank=True, null=True)
    cash_deposit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    bank_guarantee_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    deposit_notes = models.TextField(blank=True, null=True)
    lease_documentation_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    late_payment_interest_percentage = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tenant_lessee.tenant_name

    def get_absolute_url(self):
        return reverse_lazy('manager:tenant_lease_detail',
                            kwargs={'pk': self.pk, 'prop': self.tenant_lessee.property.pk, 'ten': self.tenant_lessee.pk})


@receiver(post_save, sender=Lease)
def lease_created_callback(sender, instance, created, *args, **kwargs):
    if created:
        Tenant.objects.filter(id=instance.tenant_lessee.id).update(lease=instance)

