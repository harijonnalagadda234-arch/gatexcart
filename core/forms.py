from django import forms
from .models import ContactMessage, QuoteRequest


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ContactForm(StyledModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }


class QuoteForm(StyledModelForm):
    class Meta:
        model = QuoteRequest
        fields = ["name", "company", "email", "phone", "country", "product", "quantity", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }
