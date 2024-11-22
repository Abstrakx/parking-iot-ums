from django.db import models
from django.core.files import File
from django.conf import settings
from model_utils import FieldTracker    
from io import BytesIO
import qrcode
import os

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
    
    # Field tracker untuk melacak perubahan field tertentu
    tracker = FieldTracker(fields=['nama', 'fakultas', 'merk_kendaraan', 'plat_nomor'])

    def save(self, *args, **kwargs):
        # Variabel nama depan mahasiswa untuk identitas
        nama_depan = self.nama.split()[0]

        # Logika untuk QR mahasiswa
        if not self.qr_code or self._state.adding or self.tracker.has_changed('nama') or self.tracker.has_changed('fakultas'):
            # Hapus file QR mahasiswa lama
            if self.qr_code:
                qr_path = os.path.join(settings.MEDIA_ROOT, self.qr_code.name)
                if os.path.exists(qr_path):
                    os.remove(qr_path)
                self.qr_code.delete(save=False)

            # Generate QR mahasiswa baru
            qrcode_img = qrcode.make(f'{self.nim}-{nama_depan}-{self.fakultas}')
            qr_io = BytesIO()
            qrcode_img.save(qr_io, 'PNG')
            qr_file = File(qr_io, name=f'{self.nim}-{nama_depan}-{self.fakultas}.png')
            self.qr_code.save(qr_file.name, qr_file, save=False)

        # Logika untuk QR kendaraan
        if (not self.qr_code_kendaraan or self._state.adding or 
            self.tracker.has_changed('merk_kendaraan') or self.tracker.has_changed('plat_nomor')):
            # Hapus file QR kendaraan lama
            if self.qr_code_kendaraan:
                qr_kendaraan_path = os.path.join(settings.MEDIA_ROOT, self.qr_code_kendaraan.name)
                if os.path.exists(qr_kendaraan_path):
                    os.remove(qr_kendaraan_path)
                self.qr_code_kendaraan.delete(save=False)

            # Generate QR kendaraan baru
            qrcode_img_kendaraan = qrcode.make(f'{self.merk_kendaraan}-{self.plat_nomor}-{self.nim}')
            qr_io_kendaraan = BytesIO()
            qrcode_img_kendaraan.save(qr_io_kendaraan, 'PNG')
            qr_kendaraan_file = File(qr_io_kendaraan, name=f'{self.merk_kendaraan}-{self.plat_nomor}-{self.nim}.png')
            self.qr_code_kendaraan.save(qr_kendaraan_file.name, qr_kendaraan_file, save=False)

        # Simpan objek ke database
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.nama} ({self.nim})"
