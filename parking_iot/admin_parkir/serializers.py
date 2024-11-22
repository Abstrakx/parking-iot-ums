from rest_framework import serializers
from .models import mahasiswa

class mahasiswaSerializer(serializers.ModelSerializer):
    class Meta:
        model = mahasiswa
        fields = '__all__'