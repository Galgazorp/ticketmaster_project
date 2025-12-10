from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from .models import SavedEvent


class SearchForm(forms.Form):
    classification = forms.ChoiceField(
        choices=[
            ('Music', 'Music'),
            ('Sports', 'Sports'),
            ('Arts & Theatre', 'Arts & Theatre'),
            ('Film', 'Film'),
            ('Miscellaneous', 'Miscellaneous'),
            ('Comedy', 'Comedy'),
            ('Family', 'Family'),
            ('Dance', 'Dance'),
        ],
        label='Genre',
        required=False  # Changed to False to remove asterisk
    )
    city = forms.CharField(
        max_length=100,
        label='City',
        required=False,  # Changed to False to remove asterisk
        widget=forms.TextInput(attrs={'placeholder': 'Hartford'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('classification', css_class='mb-3'),
            Field('city', css_class='mb-3')
        )

    def clean(self):
        """Custom validation to still require both fields"""
        cleaned_data = super().clean()
        classification = cleaned_data.get('classification')
        city = cleaned_data.get('city')

        if not classification:
            self.add_error('classification', 'Please select a genre.')
        if not city:
            self.add_error('city', 'Please enter a city.')

        return cleaned_data


class EditEventNotesForm(forms.ModelForm):
    class Meta:
        model = SavedEvent
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add your notes here...'})
        }
        labels = {
            'notes': 'Event Notes'
        }