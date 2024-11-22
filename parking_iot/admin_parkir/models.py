from django.db import models
from django.core.files import File
from io import BytesIO
import qrcode

class mahasiswa(models.Model):
    nim = models.CharField(max_length=10, primary_key=True)
    nama = models.CharField(max_length=50)
    fakultas = models.CharField(max_length=50)
    jurusan = models.CharField(max_length=20)
    no_hp = models.CharField(max_length=20)
    merk_kendaraan = models.CharField(max_length=20, default='Tidak Ada')
    plat_nomor = models.CharField(max_length=20, default='Tidak Ada')
    qr_code = models.ImageField(upload_to='qr_code_mahasiswa/', blank=True, null=True)
    qr_code_kendaraan = models.ImageField(upload_to='qr_code_kendaraan/', blank=True, null=True)
    last_out = models.JSONField(default=list)
    screenshots = models.JSONField(default=list)
    
    def save(self, *args, **kwargs):
        # Variabel nama pertama mahasiswa untuk identitas 
        nama_depan = self.nama.split()[0]

        # Membuat QR Code Identitas yang auto generate
        qrcode_img = qrcode.make(f'{self.nim}-{nama_depan}-{self.fakultas}')
        qr_io = BytesIO()
        qrcode_img.save(qr_io, 'PNG')
        qrcode_file = File(qr_io, name=f'{self.nim}-{nama_depan}-{self.fakultas}.png')
        self.qr_code.save(qrcode_file.name, qrcode_file, save=False)

        # Membuat QR Code untuk identitas kendaraan mahasiswa
        qrcode_img_kendaraan = qrcode.make(f'{self.merk_kendaraan}-{self.plat_nomor}-{self.nim}')
        qr_io_kendaraan = BytesIO()
        qrcode_img_kendaraan.save(qr_io_kendaraan, 'PNG')
        qrcode_kendaraan_file = File(qr_io_kendaraan, name=f'{self.merk_kendaraan}-{self.plat_nomor}-{self.nim}.png')
        self.qr_code_kendaraan.save(qrcode_kendaraan_file.name, qrcode_kendaraan_file, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama} ({self.nim})"
