from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.core.files import File
from rest_framework import viewsets
import os
from io import BytesIO
import qrcode
from .models import mahasiswa
from .models import mahasiswa as Mahasiswa
from .serializers import mahasiswaSerializer
from .forms import mahasiswaForm

class mahasiswaViewSet(viewsets.ModelViewSet):
    queryset = mahasiswa.objects.all()
    serializer_class = mahasiswaSerializer

class CustomLoginView(LoginView):
    template_name = 'html/login.html'

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)

@login_required(login_url='login')
def dashboard_mahasiswa_list(request):
    mahasiswas = mahasiswa.objects.all()
    if not mahasiswas.exists():
        mahasiswas = None
    
    if request.method == 'POST':
        form = mahasiswaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  
        else:
            print(form.errors)
    else:
        form = mahasiswaForm()

    paginator = Paginator(mahasiswas, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'mahasiswas': mahasiswas,
        'page_obj': page_obj
    }

    return render(request, 'html/dashboard_template.html', context)

@login_required(login_url='login')
def delete_mahasiswa(request):
    if request.method == 'POST':
        nim = request.POST.get('nim')
        try:
            student = mahasiswa.objects.get(nim=nim)

            # Delete QR code for mahasiswa if it exists
            if student.qr_code:
                qr_mahasiswa_path = os.path.join(settings.BASE_DIR, student.qr_code.name)
                if os.path.exists(qr_mahasiswa_path):
                    os.remove(qr_mahasiswa_path)

            # Delete QR code for kendaraan if it exists
            if student.qr_code_kendaraan:
                qr_kendaraan_path = os.path.join(settings.BASE_DIR, student.qr_code_kendaraan.name)
                if os.path.exists(qr_kendaraan_path):
                    os.remove(qr_kendaraan_path)

            student.delete()
            messages.success(request, 'Data mahasiswa berhasil dihapus.')
        except mahasiswa.DoesNotExist:
            messages.error(request, 'Data mahasiswa tidak ditemukan.')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            
    return redirect('dashboard')

@login_required(login_url='login')
def edit_mahasiswa(request):
    if request.method == 'POST':
        nim = request.POST.get('nim')
        try:
            mahasiswa = Mahasiswa.objects.get(nim=nim)

            # Perbarui data mahasiswa
            mahasiswa.nama = request.POST.get('nama')
            mahasiswa.fakultas = request.POST.get('fakultas')
            mahasiswa.jurusan = request.POST.get('jurusan')
            mahasiswa.no_hp = request.POST.get('no_hp')
            mahasiswa.merk_kendaraan = request.POST.get('merk_kendaraan')
            mahasiswa.plat_nomor = request.POST.get('plat_nomor')

            # Hanya memanggil save untuk menangani semua proses di model
            mahasiswa.save()

            messages.success(request, 'Mahasiswa updated successfully')
            return redirect('dashboard')

        except Mahasiswa.DoesNotExist:
            messages.error(request, 'Mahasiswa not found')
            return redirect('dashboard')

    return redirect('dashboard')
