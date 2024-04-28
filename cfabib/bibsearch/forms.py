from django import forms
from django.forms import ModelMultipleChoiceField
#from uploads.core.models import Document
from users.models import CustomUser, Bibgroup

from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple

from django.db.models.fields import BLANK_CHOICE_DASH


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit


class DevkeyForm(forms.Form):
    inputDevKey = forms.CharField(label="ADS API Token", max_length=250,required=False)

    class Meta:
        model = CustomUser
        fields = ('devkey',)


class BibgroupForm(forms.Form):
    inputBibgroup = forms.ModelChoiceField(empty_label='----', queryset=Bibgroup.objects.values_list("bibgroup", flat=True).distinct(), label="Bibgroup",required=False)

    class Meta:
        model = CustomUser
        fields = ('bibgroup',)



#forms.ChoiceField(choices=BLANK_CHOICE_DASH + list(Bibgroup.objects.values_list("bibgroup", flat=True)), label="Bibgroup", required=False)

# class LocationChoiceField(forms.Form):

#     locations = forms.ModelChoiceField(
#         queryset=Bibgroup.objects.values_list("bibgroup", flat=True).distinct(),
#         empty_label=None
#     )