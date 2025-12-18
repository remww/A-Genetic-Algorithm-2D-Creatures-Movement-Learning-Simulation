"""
步履蹣跚：基於物理引擎的 2D 生物行走演化
錄影模組 - 使用 imageio 錄製 MP4
"""

import pygame
import numpy as np
from datetime import datetime
from config import *

try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False
    print("Warning: imageio not available. Recording disabled.")


class Recorder:
    """
    錄影器

    使用 imageio-ffmpeg 將 Pygame 畫面錄製成 MP4
    """

    def __init__(self):
        """初始化錄影器"""
        self.is_recording = False
        self.writer = None
        self.filename = None
        self.frame_count = 0
        self.frame_interval = FPS // RECORDING_FPS  # 每幾幀錄一次

    def start_recording(self, filename: str = None):
        """
        開始錄影

        Args:
            filename: 輸出檔名（如果為 None 則自動生成）
        """
        if not IMAGEIO_AVAILABLE:
            print("Cannot start recording: imageio not available")
            return False

        if self.is_recording:
            print("Already recording!")
            return False

        # 生成檔名
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = f"evolution_{timestamp}.mp4"
        else:
            self.filename = filename

        try:
            # 創建 writer
            self.writer = imageio.get_writer(
                self.filename,
                fps=RECORDING_FPS,
                codec='libx264',
                quality=8,  # 0-10, 10 is best
                pixelformat='yuv420p',  # 確保相容性
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
        """停止錄影"""
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
        """
        添加一幀到錄影

        Args:
            surface: Pygame Surface 物件
        """
        if not self.is_recording or self.writer is None:
            return

        # 只在特定間隔錄製（降低檔案大小）
        self.frame_count += 1
        if self.frame_count % self.frame_interval != 0:
            return

        try:
            # 將 Pygame Surface 轉換為 numpy array
            # Pygame 使用 (width, height, channels) 格式，需要轉置
            frame_data = pygame.surfarray.array3d(surface)
            # 轉換為 (height, width, channels) 格式
            frame_data = np.transpose(frame_data, (1, 0, 2))
            # 寫入幀
            self.writer.append_data(frame_data)
        except Exception as e:
            print(f"Error adding frame: {e}")

    def toggle_recording(self, filename: str = None) -> bool:
        """
        切換錄影狀態

        Returns:
            新的錄影狀態
        """
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording(filename)
        return self.is_recording

    def __del__(self):
        """確保錄影被正確關閉"""
        if self.is_recording:
            self.stop_recording()
