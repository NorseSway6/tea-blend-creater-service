from django import forms
from .models import *
from django.db.models import Min, Count

class TeaBlendForm(forms.Form):
    theme = forms.ModelChoiceField(
        label='Тема купажа',
        queryset= Theme.objects.order_by('name'),
        empty_label='Выберите тему купажа',
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )
    
    taste_type = forms.ModelChoiceField(
        label='Предпочтительный вкус',
        queryset=Subtaste.objects.none(),
        empty_label='Выберите желаемый вкус',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )
    
    tea_type = forms.ChoiceField(
        label='Тип чая для основы',
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    no_additives = forms.BooleanField(
        label='Без добавок',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    price_range = forms.IntegerField(
        label='Ценовой диапазон',
        min_value=100,
        max_value=3000,
        initial=1000,
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'class': 'form-range',
            'oninput': 'updatePriceValue(this.value)'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        tea_types = BaseTea.objects.values_list('tea_type', flat=True).distinct()

        subtastes = Subtaste.objects.values('name').annotate(min_id=Min('id'),count=Count('id')).order_by('name')
        subtaste_ids = [item['min_id'] for item in subtastes]
        subtaste_objects = Subtaste.objects.filter(id__in=subtaste_ids).order_by('name')
        
        self.fields['taste_type'].queryset = subtaste_objects
        
        self.fields['tea_type'].choices = [(t, t) for t in tea_types]