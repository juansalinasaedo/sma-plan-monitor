# apps/medidas/forms.py
from django import forms
from .models import RegistroAvance


class RegistroAvanceForm(forms.ModelForm):
    class Meta:
        model = RegistroAvance
        fields = ['medida', 'fecha_registro', 'porcentaje_avance', 'descripcion', 'evidencia']
        widgets = {
            'fecha_registro': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        organismo = kwargs.pop('organismo', None)
        super().__init__(*args, **kwargs)

        if organismo:
            # Filtrar medidas asignadas al organismo
            self.fields['medida'].queryset = organismo.medidas_asignadas.all()