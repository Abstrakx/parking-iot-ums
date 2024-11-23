from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from rest_framework import viewsets
import os
import cv2
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
        'page_obj': page_obj,
        'request': request,
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

@csrf_exempt
def detect_qr_code(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            received_qr_code = request.POST.get('qr_code', '')
            timestamp = request.POST.get('timestamp', '')
            screenshot = request.FILES.get('screenshot', None)

            # Extract NIM from received QR code
            try:
                received_nim = received_qr_code.split('-')[0]
            except IndexError:
                return JsonResponse({'error': 'Invalid QR code format'}, status=400)

            print(f"Received NIM: {received_nim}")
            
            # Find matching student by NIM
            try:
                mahasiswa = Mahasiswa.objects.filter(qr_code__icontains=received_nim).first()
                if not mahasiswa:
                    return JsonResponse({'error': 'Student not found with provided NIM'}, status=404)
                
                # Get the QR code path from static files
                qr_image_path = os.path.join(settings.BASE_DIR, 'qr_code_mahasiswa', str(mahasiswa.qr_code).split('/')[-1])
                
                # Read QR code from stored image using OpenCV
                if os.path.exists(qr_image_path):
                    # Read the image
                    stored_image = cv2.imread(qr_image_path)
                    if stored_image is None:
                        return JsonResponse({
                            'error': 'Failed to read stored QR image',
                            'path': qr_image_path
                        }, status=500)
                    
                    # Initialize QR code detector
                    qr_detector = cv2.QRCodeDetector()
                    
                    # Detect and decode QR code
                    stored_qr_data, bbox, _ = qr_detector.detectAndDecode(stored_image)
                    
                    if not stored_qr_data:
                        return JsonResponse({
                            'error': 'Could not detect QR code in stored image',
                            'path': qr_image_path
                        }, status=500)
                    
                    print(f"Stored QR Data: {stored_qr_data}")
                    print(f"Received QR Data: {received_qr_code}")
                    
                    # Compare the QR codes
                    if stored_qr_data != received_qr_code:
                        return JsonResponse({
                            'error': 'QR code mismatch',
                            'stored': stored_qr_data,
                            'received': received_qr_code
                        }, status=400)
                else:
                    return JsonResponse({
                        'error': 'Stored QR image not found',
                        'path': qr_image_path
                    }, status=404)

            except Exception as e:
                return JsonResponse({
                    'error': f'Error validating QR code: {str(e)}',
                    'qr_code': str(mahasiswa.qr_code) if mahasiswa else 'No mahasiswa found'
                }, status=400)

            # Update Mahasiswa data
            last_out_entry = {
                "datetime": timestamp,
                "screenshot": None,
            }

            # Save the screenshot if provided
            if screenshot:
                screenshot_filename = f'{received_nim}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
                screenshot_path = os.path.join(settings.BASE_DIR, 'screenshots', screenshot_filename)
                
                # Ensure screenshots directory exists
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                
                with open(screenshot_path, 'wb') as f:
                    for chunk in screenshot.chunks():
                        f.write(chunk)
                last_out_entry["screenshot"] = f'screenshots/{screenshot_filename}'

            # Update JSONField for last_out
            if not mahasiswa.last_out:
                mahasiswa.last_out = []
            mahasiswa.last_out.append(last_out_entry)
            mahasiswa.save()

            return JsonResponse({
                'message': 'QR code validated and data saved successfully',
                'student': {
                    'nim': received_nim,
                    'name': mahasiswa.nama if hasattr(mahasiswa, 'nama') else None
                }
            })

        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def mahasiswa_detail(request, nim):
    mahasiswa = get_object_or_404(Mahasiswa, nim=nim)  
    return render(request, 'html/dashboard_mahasiswa.html', {'mahasiswa': mahasiswa})