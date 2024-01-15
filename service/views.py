from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from PIL import Image
import rembg
import base64
from io import BytesIO
import uuid  # Import the uuid module
from django.conf import settings
from django.core.files.storage import default_storage
import os
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage


@api_view(['POST'])
def remove_background_api(request):
    if 'image' not in request.FILES:
        return HttpResponseBadRequest('Image not provided')
    # Get the image from the request
    image = request.FILES['image']
    # Check if the image is in HEIC format and convert it to JPG
    if image.name.lower().endswith('.heic'):
        register_heif_opener()
        img = Image.open(image)
        image = img.convert('RGB')

    try:
        # Read the image data
        image_data = image.read()
        # Remove background using rembg
        output = rembg.remove(image_data)
        # Create an in-memory image object from the processed data
        processed_image = Image.open(BytesIO(output))

        # Convert the processed image to base64 format
        buffered = BytesIO()
        processed_image.save(buffered, format="PNG")
        processed_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
         # Generate a unique filename using uuid
        unique_filename = f"processed_image_{uuid.uuid4().hex}.png"
        file_path = os.path.join(settings.MEDIA_ROOT, unique_filename)
        
        # Save the processed image on the server with the unique filename
        with default_storage.open(file_path, 'wb') as destination:
            processed_image.save(destination, format="PNG")
        
        
        # Generate a relative URL for the saved image
        relative_url = default_storage.url(file_path.replace(settings.MEDIA_ROOT, ''))

        # Generate the full URL with the host
        full_url = request.build_absolute_uri(relative_url)

        # Return the full URL of the processed image
        return Response({'image_url': full_url}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
