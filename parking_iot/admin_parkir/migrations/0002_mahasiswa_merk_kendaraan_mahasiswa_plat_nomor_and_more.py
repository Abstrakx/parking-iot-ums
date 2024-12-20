# Generated by Django 4.2.6 on 2024-11-21 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_parkir', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mahasiswa',
            name='merk_kendaraan',
            field=models.CharField(default='Tidak Ada', max_length=20),
        ),
        migrations.AddField(
            model_name='mahasiswa',
            name='plat_nomor',
            field=models.CharField(default='Tidak Ada', max_length=10),
        ),
        migrations.AddField(
            model_name='mahasiswa',
            name='qr_code_kendaraan',
            field=models.ImageField(blank=True, null=True, upload_to='qr_code_kendaraan/'),
        ),
        migrations.AlterField(
            model_name='mahasiswa',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='qr_code_mahasiswa/'),
        ),
    ]
