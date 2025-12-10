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
        required=True
    )
    city = forms.CharField(
        max_length=100,
        label='City',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Hartford'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False  # Don't let crispy render the form tag
        self.helper.form_show_labels = True
        self.helper.form_show_errors = True
        # Hide the asterisks for required fields
        self.helper.label_class = ''
        self.helper.field_class = ''
        self.helper.layout = Layout(
            Field('classification', css_class='mb-3'),
            Field('city', css_class='mb-3')
        )
        # Remove the asterisk from labels
        for field_name in self.fields:
            self.fields[field_name].label_suffix = ''


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