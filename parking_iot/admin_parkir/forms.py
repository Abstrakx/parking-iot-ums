from django import forms
from .models import mahasiswa

class mahasiswaForm(forms.ModelForm):
    class Meta:
        model = mahasiswa
        fields = ['nim', 'nama', 'fakultas', 'jurusan', 'no_hp', 'merk_kendaraan', 'plat_nomor']
