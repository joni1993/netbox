from django import forms
from django.utils.translation import gettext as _

from dcim.models import Location, Rack, Region, Site, SiteGroup
from extras.forms import CustomFieldModelFilterForm
from ipam.choices import *
from ipam.constants import *
from ipam.models import *
from ipam.models import ASN
from tenancy.forms import TenancyFilterForm
from utilities.forms import (
    add_blank_choice, DynamicModelChoiceField, DynamicModelMultipleChoiceField, StaticSelect, StaticSelectMultiple,
    TagFilterField, BOOLEAN_WITH_BLANK_CHOICES,
)

__all__ = (
    'AggregateFilterForm',
    'ASNFilterForm',
    'FHRPGroupFilterForm',
    'IPAddressFilterForm',
    'IPRangeFilterForm',
    'PrefixFilterForm',
    'RIRFilterForm',
    'RoleFilterForm',
    'RouteTargetFilterForm',
    'ServiceFilterForm',
    'VLANFilterForm',
    'VLANGroupFilterForm',
    'VRFFilterForm',
)

PREFIX_MASK_LENGTH_CHOICES = add_blank_choice([
    (i, i) for i in range(PREFIX_LENGTH_MIN, PREFIX_LENGTH_MAX + 1)
])

IPADDRESS_MASK_LENGTH_CHOICES = add_blank_choice([
    (i, i) for i in range(IPADDRESS_MASK_LENGTH_MIN, IPADDRESS_MASK_LENGTH_MAX + 1)
])


class VRFFilterForm(TenancyFilterForm, CustomFieldModelFilterForm):
    model = VRF
    field_groups = [
        ['q', 'tag'],
        ['import_target_id', 'export_target_id'],
        ['tenant_group_id', 'tenant_id'],
    ]
    import_target_id = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False,
        label=_('Import targets'),
        fetch_trigger='open'
    )
    export_target_id = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False,
        label=_('Export targets'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


class RouteTargetFilterForm(TenancyFilterForm, CustomFieldModelFilterForm):
    model = RouteTarget
    field_groups = [
        ['q', 'tag'],
        ['importing_vrf_id', 'exporting_vrf_id'],
        ['tenant_group_id', 'tenant_id'],
    ]
    importing_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Imported by VRF'),
        fetch_trigger='open'
    )
    exporting_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Exported by VRF'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


class RIRFilterForm(CustomFieldModelFilterForm):
    model = RIR
    is_private = forms.NullBooleanField(
        required=False,
        label=_('Private'),
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class AggregateFilterForm(TenancyFilterForm, CustomFieldModelFilterForm):
    model = Aggregate
    field_groups = [
        ['q', 'tag'],
        ['family', 'rir_id'],
        ['tenant_group_id', 'tenant_id']
    ]
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family'),
        widget=StaticSelect()
    )
    rir_id = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


class ASNFilterForm(TenancyFilterForm, CustomFieldModelFilterForm):
    model = ASN
    field_groups = [
        ['q'],
        ['rir_id'],
        ['tenant_group_id', 'tenant_id'],
        ['site_id'],
    ]
    rir_id = DynamicModelMultipleChoiceField(
        queryset=RIR.objects.all(),
        required=False,
        label=_('RIR'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Site'),
        fetch_trigger='open'
    )


class RoleFilterForm(CustomFieldModelFilterForm):
    model = Role
    tag = TagFilterField(model)


class PrefixFilterForm(TenancyFilterForm, CustomFieldModelFilterForm):
    model = Prefix
    field_groups = [
        ['q', 'tag'],
        ['within_include', 'family', 'status', 'role_id', 'mask_length', 'is_pool', 'mark_utilized'],
        ['vrf_id', 'present_in_vrf_id'],
        ['region_id', 'site_group_id', 'site_id'],
        ['tenant_group_id', 'tenant_id']
    ]
    mask_length__lte = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    within_include = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Prefix',
            }
        ),
        label=_('Search within')
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family'),
        widget=StaticSelect()
    )
    mask_length = forms.MultipleChoiceField(
        required=False,
        choices=PREFIX_MASK_LENGTH_CHOICES,
        label=_('Mask length'),
        widget=StaticSelectMultiple()
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Assigned VRF'),
        null_option='Global',
        fetch_trigger='open'
    )
    present_in_vrf_id = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Present in VRF'),
        fetch_trigger='open'
    )
    status = forms.MultipleChoiceField(
        choices=PrefixStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        null_option='None',
        label=_('Role'),
        fetch_trigger='open'
    )
    is_pool = forms.NullBooleanField(
        required=False,
        label=_('Is a pool'),
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mark_utilized = forms.NullBooleanField(
        required=False,
        label=_('Marked as 100% utilized'),
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class IPRangeFilterForm(TenancyFilterForm, CustomFieldModelFilterForm):
    model = IPRange
    field_groups = [
        ['q', 'tag'],
        ['family', 'vrf_id', 'status', 'role_id'],
        ['tenant_group_id', 'tenant_id'],
    ]
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family'),
        widget=StaticSelect()
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Assigned VRF'),
        null_option='Global',
        fetch_trigger='open'
    )
    status = forms.MultipleChoiceField(
        choices=PrefixStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        null_option='None',
        label=_('Role'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


class IPAddressFilterForm(TenancyFilterForm, CustomFieldModelFilterForm):
    model = IPAddress
    field_order = [
        'q', 'parent', 'family', 'mask_length', 'vrf_id', 'present_in_vrf_id', 'status', 'role',
        'assigned_to_interface', 'tenant_group_id', 'tenant_id',
    ]
    field_groups = [
        ['q', 'tag'],
        ['parent', 'family', 'status', 'role', 'mask_length', 'assigned_to_interface'],
        ['vrf_id', 'present_in_vrf_id'],
        ['tenant_group_id', 'tenant_id'],
    ]
    parent = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Prefix',
            }
        ),
        label='Parent Prefix'
    )
    family = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressFamilyChoices),
        label=_('Address family'),
        widget=StaticSelect()
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=IPADDRESS_MASK_LENGTH_CHOICES,
        label=_('Mask length'),
        widget=StaticSelect()
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Assigned VRF'),
        null_option='Global',
        fetch_trigger='open'
    )
    present_in_vrf_id = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('Present in VRF'),
        fetch_trigger='open'
    )
    status = forms.MultipleChoiceField(
        choices=IPAddressStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    role = forms.MultipleChoiceField(
        choices=IPAddressRoleChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    assigned_to_interface = forms.NullBooleanField(
        required=False,
        label=_('Assigned to an interface'),
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class FHRPGroupFilterForm(CustomFieldModelFilterForm):
    model = FHRPGroup
    field_groups = (
        ('q', 'tag'),
        ('protocol', 'group_id'),
        ('auth_type', 'auth_key'),
    )
    protocol = forms.MultipleChoiceField(
        choices=FHRPGroupProtocolChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    group_id = forms.IntegerField(
        min_value=0,
        required=False,
        label='Group ID'
    )
    auth_type = forms.MultipleChoiceField(
        choices=FHRPGroupAuthTypeChoices,
        required=False,
        widget=StaticSelectMultiple(),
        label='Authentication type'
    )
    auth_key = forms.CharField(
        required=False,
        label='Authentication key'
    )
    tag = TagFilterField(model)


class VLANGroupFilterForm(CustomFieldModelFilterForm):
    field_groups = [
        ['q', 'tag'],
        ['region', 'sitegroup', 'site', 'location', 'rack']
    ]
    model = VLANGroup
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    sitegroup = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Site'),
        fetch_trigger='open'
    )
    location = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_('Location'),
        fetch_trigger='open'
    )
    rack = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label=_('Rack'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


class VLANFilterForm(TenancyFilterForm, CustomFieldModelFilterForm):
    model = VLAN
    field_groups = [
        ['q', 'tag'],
        ['region_id', 'site_group_id', 'site_id'],
        ['group_id', 'status', 'role_id', 'vid'],
        ['tenant_group_id', 'tenant_id'],
    ]
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region': '$region'
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region': '$region'
        },
        label=_('VLAN group'),
        fetch_trigger='open'
    )
    status = forms.MultipleChoiceField(
        choices=VLANStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        null_option='None',
        label=_('Role'),
        fetch_trigger='open'
    )
    vid = forms.IntegerField(
        required=False,
        label='VLAN ID'
    )
    tag = TagFilterField(model)


class ServiceFilterForm(CustomFieldModelFilterForm):
    model = Service
    field_groups = (
        ('q', 'tag'),
        ('protocol', 'port'),
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelectMultiple()
    )
    port = forms.IntegerField(
        required=False,
    )
    tag = TagFilterField(model)
