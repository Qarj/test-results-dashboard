from django import forms
from .models import Artefact

class ArtefactForm(forms.ModelForm):
    class Meta:
        model = Artefact
        fields = (
            'test_name',
            'app_name',
            'run_name',
            'name',
            'desc',
            'document',
        )