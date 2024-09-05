from moviepy.config import change_settings


change_settings({"FFMPEG_BINARY": r"C:/ffmpeg-win64-v4.2.2.exe"})


import os

import wave
import math
import numpy as np
import speech_recognition as sr
from moviepy.editor import VideoFileClip

def convert_video_to_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')

def enhance_audio(input_audio_file, output_audio_file, volume_gain=1.5):
    with wave.open(input_audio_file, 'rb') as audio:
        params = audio.getparams()
        num_frames = audio.getnframes()
        
        with wave.open(output_audio_file, 'wb') as output_audio:
            output_audio.setparams(params)
            frames_per_read = 1024
            for _ in range(0, num_frames, frames_per_read):
                frames = audio.readframes(frames_per_read)
                enhanced_frames = enhance_audio_frames(frames, params.sampwidth, volume_gain)
                output_audio.writeframes(enhanced_frames)

def enhance_audio_frames(frames, sampwidth, volume_gain):
    if sampwidth == 1:
        audio_samples = np.frombuffer(frames, dtype=np.uint8) - 128
    elif sampwidth == 2:
        audio_samples = np.frombuffer(frames, dtype=np.int16)
    else:
        raise ValueError("Unsupported sample width")

    enhanced_samples = (audio_samples * volume_gain).astype(audio_samples.dtype)

    if sampwidth == 1:
        enhanced_samples = np.clip(enhanced_samples + 128, 0, 255)
    elif sampwidth == 2:
        enhanced_samples = np.clip(enhanced_samples, -32768, 32767)

    return enhanced_samples.tobytes()

def process_audio_chunk(chunk_filename, recognizer):
    try:
        with sr.AudioFile(chunk_filename) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            print(f"Processed chunk {chunk_filename}: {text}")
            return text
    except sr.UnknownValueError:
        print(f"Could not understand audio in {chunk_filename}")
        return ""
    except sr.RequestError as e:
        print(f"Request error for {chunk_filename}: {e}")
        return "[Error retrieving results]"
    except Exception as e:
        print(f"Error processing chunk {chunk_filename}: {e}")
        return "[Processing error]"

def audio_to_text(input_audio_file, output_text_file, chunk_duration=60):
    recognizer = sr.Recognizer()
    
    try:
        with wave.open(input_audio_file, 'rb') as audio:
            params = audio.getparams()
            frame_rate = params.framerate
            n_channels = params.nchannels
            sampwidth = params.sampwidth
            n_frames = audio.getnframes()

            chunk_size = int(frame_rate * chunk_duration)
            total_chunks = math.ceil(n_frames / chunk_size)

            with open(output_text_file, 'w') as output_file:
                for i in range(total_chunks):
                    chunk_filename = f"chunk_{i}.wav"
                    print(f"Creating chunk {chunk_filename}...")  # Debugging log
                    with wave.open(chunk_filename, 'wb') as chunk:
                        chunk.setnchannels(n_channels)
                        chunk.setsampwidth(sampwidth)
                        chunk.setframerate(frame_rate)
                        frames = audio.readframes(chunk_size)
                        chunk.writeframes(frames)

                    text = process_audio_chunk(chunk_filename, recognizer)
                    output_file.write(text + "\n")
                    os.remove(chunk_filename)
                    print(f"Processed chunk {chunk_filename} and wrote text.")  # Debugging log
            
            print(f"Text output file saved to {output_text_file}")

    except Exception as e:
        print(f"Error in audio_to_text function: {e}")

def process_video(video_path, output_folder):
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    audio_path = os.path.join(output_folder, f"{base_name}_temp.wav")
    enhanced_audio_path = os.path.join(output_folder, f"{base_name}_enhanced_temp.wav")
    output_text_file = os.path.join(output_folder, f"{base_name}.txt")

    convert_video_to_audio(video_path, audio_path)
    enhance_audio(audio_path, enhanced_audio_path)
    audio_to_text(enhanced_audio_path, output_text_file)

    os.remove(audio_path)
    os.remove(enhanced_audio_path)

    return output_text_file

def process_videos_in_folder(video_folder, output_folder):
    for filename in os.listdir(video_folder):
        if filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            video_path = os.path.join(video_folder, filename)
            process_video(video_path, output_folder)
