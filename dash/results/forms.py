from django import forms
from .models import Artifact

class ArtifactForm(forms.ModelForm):
    class Meta:
        model = Artifact
        fields = (
            'test_name',
            'app_name',
            'run_name',
            'name',
            'desc',
            'document',
             )