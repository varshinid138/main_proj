
from io import BytesIO
from moviepy.config import change_settings
from reportlab.pdfgen import canvas  # For creating PDFs
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak  # Import the required classes
from reportlab.lib.styles import getSampleStyleSheet

from moviepy.editor import VideoFileClip
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from .models import Video
from .forms import VideoForm
from .vtx import  process_video
import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

os.environ["FFMPEG_BINARY"] = r"C:\ffmpeg-win64-v4.2.2.exe"

def index(request):
    # Path to the video folder in the media directory
    video_folder = os.path.join(settings.MEDIA_ROOT, 'videos')
    
    # List of video files in the folder with .mp4 or .mkv extensions
    video_files = [
        f for f in os.listdir(video_folder) 
        if os.path.isfile(os.path.join(video_folder, f)) and f.lower().endswith(('.mp4', '.mkv'))
    ]
    
    # Create a list of tuples (video_name, video_url)
    video_urls = [
        (video_file, os.path.join(settings.MEDIA_URL, 'videos', video_file)) 
        for video_file in video_files
    ]
    
    # Handle case when no videos are available
    if not video_urls:
        video_urls = [('No videos available.', '')]
    
    # Render the template with the video URLs
    return render(request, 'converter/index.html', {'videos': video_urls})


@csrf_exempt
@require_POST
def convert_video(request):
    data = json.loads(request.body)
    video_url = data.get('video_url')
    
    if not video_url:
        return JsonResponse({"success": False, "message": "Video URL is required"}, status=400)
    
    video_path = os.path.join(settings.MEDIA_ROOT, 'videos', os.path.basename(video_url))
    
    try:
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_folder = os.path.join(settings.MEDIA_ROOT, 'converted')
        output_text_path = os.path.join(output_folder, f"{video_name}.txt")
        
        # Process the video to convert to text
        process_video(video_path, output_folder)
        
        # Check if the converted text file exists
        if not os.path.exists(output_text_path):
            return JsonResponse({"success": False, "message": "Converted text file not found"}, status=404)
        
        # Return the URL to download the text file
        download_url = f"{settings.MEDIA_URL}converted/{video_name}.txt"
        return JsonResponse({"success": True, "message": "Process completed", "text_url": download_url})
    
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
def converted_text(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return JsonResponse({"success": False, "message": "Video not found"}, status=404)
    
    if video.converted_text:
        file_path = video.converted_text.path
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                text = file.read()
            return render(request, 'converter/converted_text.html', {'text': text})
        else:
            return JsonResponse({"success": False, "message": "Converted text file not found"}, status=404)
    else:
        return JsonResponse({"success": False, "message": "Video has not been converted yet"}, status=400)
