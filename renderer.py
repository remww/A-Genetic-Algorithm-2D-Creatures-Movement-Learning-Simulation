import pygame
import math
from config import *

class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.camera_offsets = [0.0] * GRID_COUNT

    def render(self, creatures: list, generation: int, best_fitness: float, current_time: float, is_paused: bool, is_recording: bool, speed_multiplier: int = 1):
        # 清空畫面
        self.screen.fill(COLOR_BACKGROUND)

        # 繪製每個 Grid
        for i in range(min(len(creatures), GRID_COUNT)):
            self._render_grid(i, creatures[i])

        # 繪製 Grid 分隔線
        self._draw_grid_lines()

        # 繪製狀態列
        self._draw_status_bar(generation, best_fitness, current_time, is_paused, is_recording, speed_multiplier)

    def _render_grid(self, grid_index: int, creature):
        # 渲染單個 Grid
        # 計算 Grid 位置
        row = grid_index // GRID_COLS
        col = grid_index % GRID_COLS
        grid_x = col * CELL_WIDTH
        grid_y = row * CELL_HEIGHT

        # 創建 Grid 的裁剪區域
        clip_rect = pygame.Rect(grid_x, grid_y, CELL_WIDTH, CELL_HEIGHT)
        self.screen.set_clip(clip_rect)

        # 更新攝影機位置
        creature_x, _ = creature.get_position()
        self._update_camera(grid_index, creature_x, grid_x)

        # 獲取攝影機偏移
        camera_x = self.camera_offsets[grid_index]

        # 繪製背景
        pygame.draw.rect(self.screen, COLOR_BACKGROUND, clip_rect)

        # 繪製地面
        ground_y = grid_y + CELL_HEIGHT - GROUND_HEIGHT
        ground_rect = pygame.Rect(grid_x, ground_y, CELL_WIDTH, GROUND_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_GROUND, ground_rect)

        # 繪製地面刻度線
        self._draw_ground_markers(grid_x, grid_y, ground_y, camera_x)

        # 繪製生物
        self._draw_creature(creature, grid_x, grid_y, camera_x)

        # 繪製 Grid 資訊
        self._draw_grid_info(grid_index, creature, grid_x, grid_y)

        # 移除裁剪
        self.screen.set_clip(None)

    def _update_camera(self, grid_index: int, creature_x: float, grid_x: int):
        # 更新攝影機位置
        camera_x = self.camera_offsets[grid_index]

        # 計算生物在 Grid 中的相對位置
        relative_x = creature_x - camera_x

        # 如果生物超出右邊界，移動攝影機
        right_boundary = CELL_WIDTH * 0.7
        if relative_x > right_boundary:
            self.camera_offsets[grid_index] += CAMERA_SCROLL_DISTANCE

    def _draw_ground_markers(self, grid_x: int, grid_y: int, ground_y: int, camera_x: float):
        marker_spacing = 50 
        start_marker = int(camera_x / marker_spacing) * marker_spacing
        end_marker = int((camera_x + CELL_WIDTH) / marker_spacing + 1) * marker_spacing

        for marker_x in range(start_marker, end_marker, marker_spacing):
            screen_x = grid_x + (marker_x - camera_x)
            if grid_x <= screen_x < grid_x + CELL_WIDTH:
                # 繪製刻度線
                pygame.draw.line(self.screen, (100, 80, 60), (int(screen_x), ground_y), (int(screen_x), ground_y + 10), 1)

                if marker_x % 100 == 0:
                    text = self.small_font.render(str(marker_x), True, (150, 130, 110))
                    self.screen.blit(text, (int(screen_x) - 10, ground_y + 12))

    def _draw_creature(self, creature, grid_x: int, grid_y: int, camera_x: float):
        # 繪製生物
        body_info = creature.get_body_info()

        # 繪製每個身體部件
        for part_name, (body, shape) in body_info.items():
            # 決定顏色
            if not creature.is_alive:
                color = COLOR_DEAD
            elif 'torso' in part_name:
                color = COLOR_TORSO
            elif 'thigh' in part_name:
                color = COLOR_THIGH
            elif 'shin' in part_name:
                color = COLOR_SHIN
            elif 'foot' in part_name:
                color = COLOR_FOOT
            else:
                color = (200, 200, 200)

            self._draw_body_part(body, shape, color, grid_x, grid_y, camera_x)

    def _draw_body_part(self, body, shape, color: tuple, grid_x: int, grid_y: int, camera_x: float):
        # 繪製單個身體部件
        # 獲取多邊形頂點
        vertices = shape.get_vertices()

        # 轉換到螢幕座標
        screen_vertices = []
        for v in vertices:
            rotated = v.rotated(body.angle)
            # 加上物體位置
            world_x = body.position.x + rotated.x
            world_y = body.position.y + rotated.y
            # 轉換到螢幕座標
            screen_x = grid_x + (world_x - camera_x)
            screen_y = grid_y + CELL_HEIGHT - GROUND_HEIGHT - world_y
            screen_vertices.append((int(screen_x), int(screen_y)))

        # 繪製多邊形
        if len(screen_vertices) >= 3:
            pygame.draw.polygon(self.screen, color, screen_vertices)
            pygame.draw.polygon(self.screen, (255, 255, 255), screen_vertices, 1)

    def _draw_grid_info(self, grid_index: int, creature, grid_x: int, grid_y: int):
        # 生物編號
        id_text = self.small_font.render(f"#{creature.creature_id + 1}", True, COLOR_TEXT)
        self.screen.blit(id_text, (grid_x + 5, grid_y + 5))

        # 適應度
        fitness_text = self.small_font.render(f"Dist: {creature.fitness:.1f}", True, COLOR_TEXT)
        self.screen.blit(fitness_text, (grid_x + 5, grid_y + 22))

        # 狀態
        if creature.is_alive:
            time_left = SIMULATION_TIME - creature.time_alive
            status_text = self.small_font.render(f"Time: {time_left:.1f}s", True, (100, 255, 100))
        else:
            status_text = self.small_font.render("DEAD", True, COLOR_DEAD)
        self.screen.blit(status_text, (grid_x + 5, grid_y + 39))

    def _draw_grid_lines(self):
        # 繪製 Grid 分隔線
        # 垂直線
        for col in range(1, GRID_COLS):
            x = col * CELL_WIDTH
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (x, 0), (x, WINDOW_HEIGHT - 60), 2)

        # 水平線
        for row in range(1, GRID_ROWS):
            y = row * CELL_HEIGHT
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (0, y), (WINDOW_WIDTH, y), 2)

    def _draw_status_bar(self, generation: int, best_fitness: float, current_time: float, is_paused: bool, is_recording: bool, speed_multiplier: int):
        # 繪製底部狀態列
        bar_height = 50
        bar_y = WINDOW_HEIGHT - bar_height

        # 繪製狀態列背景
        pygame.draw.rect(self.screen, (40, 40, 50), (0, bar_y, WINDOW_WIDTH, bar_height))
        pygame.draw.line(self.screen, COLOR_GRID_LINE, (0, bar_y), (WINDOW_WIDTH, bar_y), 2)

        # 世代資訊
        gen_text = self.font.render(f"Generation: {generation}", True, COLOR_TEXT)
        self.screen.blit(gen_text, (20, bar_y + 15))

        # 最佳適應度
        best_text = self.font.render(f"Best Distance: {best_fitness:.1f}", True, (255, 215, 0))
        self.screen.blit(best_text, (200, bar_y + 15))

        # 模擬時間
        time_text = self.font.render(f"Time: {current_time:.1f}s", True, COLOR_TEXT)
        self.screen.blit(time_text, (450, bar_y + 15))

    def reset_cameras(self):
        # 重置所有攝影機位置
        self.camera_offsets = [0.0] * GRID_COUNT

    def get_frame(self) -> pygame.Surface:
        return self.screen.copy()