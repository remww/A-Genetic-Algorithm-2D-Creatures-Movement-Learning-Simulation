import pygame
import numpy as np
from datetime import datetime
from config import *

try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False
    print("imageio Error")

# 使用 imageio 進行錄影
class Recorder:
    def __init__(self):
        self.is_recording = False
        self.writer = None
        self.filename = None
        self.frame_count = 0
        self.frame_interval = FPS // RECORDING_FPS

    def start_recording(self, filename: str = None):
        if not IMAGEIO_AVAILABLE:
            print("imageio not available")
            return False

        if self.is_recording:
            print("Already recording!")
            return False

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = f"evolution_{timestamp}.mp4"
        else:
            self.filename = filename

        try:
            self.writer = imageio.get_writer(
                self.filename,
                fps=RECORDING_FPS,
                codec='libx264',
                quality=8, 
                pixelformat='yuv420p', 
                macro_block_size=16,
            )
            self.is_recording = True
            self.frame_count = 0
            print(f"Recording started: {self.filename}")
            return True
        except Exception as e:
            print(f"Failed to start recording: {e}")
            return False

    def stop_recording(self):
        if not self.is_recording:
            return

        try:
            if self.writer is not None:
                self.writer.close()
                self.writer = None
            self.is_recording = False
            print(f"Recording saved: {self.filename} ({self.frame_count} frames)")
        except Exception as e:
            print(f"Error stopping recording: {e}")

    def add_frame(self, surface: pygame.Surface):
        if not self.is_recording or self.writer is None:
            return

        self.frame_count += 1
        if self.frame_count % self.frame_interval != 0:
            return

        try:
            frame_data = pygame.surfarray.array3d(surface)
            frame_data = np.transpose(frame_data, (1, 0, 2))
            self.writer.append_data(frame_data)
        except Exception as e:
            print(f"Error adding frame: {e}")

    def toggle_recording(self, filename: str = None) -> bool:
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording(filename)
        return self.is_recording

    def __del__(self):
        if self.is_recording:
            self.stop_recording()