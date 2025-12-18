"""
步履蹣跚：基於物理引擎的 2D 生物行走演化
主程式
"""

import pygame
import pymunk
import sys
from config import *
from creature import Creature
from evolution import GeneticAlgorithm
from renderer import Renderer
from recorder import Recorder


class Simulation:
    """
    模擬主類別

    負責：
    - 初始化和管理 Pygame/Pymunk
    - 管理生物族群
    - 控制演化流程
    - 處理使用者輸入
    """

    def __init__(self):
        """初始化模擬"""
        # 初始化 Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("步履蹣跚 - 2D 生物行走演化")
        self.clock = pygame.time.Clock()

        # 初始化渲染器和錄影器
        self.renderer = Renderer(self.screen)
        self.recorder = Recorder()

        # 初始化遺傳演算法
        self.ga = GeneticAlgorithm()

        # 狀態變數
        self.is_running = True
        self.is_paused = False
        self.speed_multiplier = 1
        self.current_time = 0.0

        # 當前族群
        self.population_genes = []
        self.creatures = []
        self.spaces = []  # 每隻生物有獨立的物理空間
        self.ground_bodies = []

        # 統計資料
        self.best_fitness_ever = 0.0

        # 初始化第一代
        self._init_generation()

    def _create_physics_space(self) -> pymunk.Space:
        """創建一個新的物理空間"""
        space = pymunk.Space()
        space.gravity = GRAVITY
        return space

    def _add_ground(self, space: pymunk.Space) -> pymunk.Body:
        """在物理空間中添加地面"""
        ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        ground_body.position = (0, 0)

        # 創建一個很長的地面
        ground_shape = pymunk.Segment(ground_body, (-1000, 0), (100000, 0), 5)
        ground_shape.friction = GROUND_FRICTION
        ground_shape.collision_type = 3  # 地面碰撞類型

        space.add(ground_body, ground_shape)
        return ground_body

    def _init_generation(self):
        """初始化一代生物"""
        # 生成或演化基因（必須在清理之前收集適應度！）
        if not self.population_genes:
            # 第一代：隨機生成
            self.population_genes = self.ga.create_initial_population()
        else:
            # 收集適應度（在清理之前）
            fitness_scores = [c.fitness for c in self.creatures]
            # 演化
            self.population_genes = self.ga.evolve(self.population_genes, fitness_scores)

        # 清理舊的物理空間（在收集適應度之後）
        self._cleanup_creatures()

        # 重置攝影機
        self.renderer.reset_cameras()

        # 創建新的生物和物理空間
        self.creatures = []
        self.spaces = []
        self.ground_bodies = []

        for i in range(POPULATION_SIZE):
            # 創建獨立的物理空間
            space = self._create_physics_space()
            self.spaces.append(space)

            # 添加地面
            ground = self._add_ground(space)
            self.ground_bodies.append(ground)

            # 創建生物
            # 起始位置：在地面上方
            start_x = 100  # 起始 X 位置
            start_y = THIGH_LENGTH + SHIN_LENGTH + FOOT_HEIGHT + 20  # 站立高度

            creature = Creature(
                space=space,
                start_x=start_x,
                start_y=start_y,
                genes=self.population_genes[i],
                creature_id=i
            )
            self.creatures.append(creature)

        # 重置模擬時間
        self.current_time = 0.0

    def _cleanup_creatures(self):
        """清理所有生物和物理空間"""
        for creature in self.creatures:
            creature.remove_from_space()
        self.creatures.clear()
        self.spaces.clear()
        self.ground_bodies.clear()

    def _update_physics(self, dt: float):
        """更新所有物理空間"""
        for i, (space, creature) in enumerate(zip(self.spaces, self.creatures)):
            if creature.is_alive:
                # 更新物理
                for _ in range(PHYSICS_STEPS):
                    space.step(dt / PHYSICS_STEPS)

                # 更新生物狀態
                creature.update(dt, self.current_time)

                # 檢查死亡
                creature.check_death(ground_y=0)

    def _check_generation_complete(self) -> bool:
        """檢查這一代是否結束"""
        # 當所有生物都死亡或時間到達上限時結束
        all_dead = all(not c.is_alive for c in self.creatures)
        time_up = self.current_time >= SIMULATION_TIME

        return all_dead or time_up

    def _handle_events(self):
        """處理使用者輸入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

                elif event.key == pygame.K_SPACE:
                    self.is_paused = not self.is_paused

                elif event.key == pygame.K_s:
                    # 切換速度
                    if self.speed_multiplier == 1:
                        self.speed_multiplier = 2
                    elif self.speed_multiplier == 2:
                        self.speed_multiplier = 4
                    elif self.speed_multiplier == 4:
                        self.speed_multiplier = 8
                    else:
                        self.speed_multiplier = 1

                elif event.key == pygame.K_r:
                    # 切換錄影
                    self.recorder.toggle_recording()

                elif event.key == pygame.K_n:
                    # 跳到下一代
                    self._force_next_generation()

    def _force_next_generation(self):
        """強制進入下一代"""
        # 將所有存活的生物標記為死亡
        for creature in self.creatures:
            creature.is_alive = False
        # 下一幀會自動觸發新一代

    def run(self):
        """主循環"""
        print("=" * 50)
        print("步履蹣跚 - 2D 生物行走演化")
        print("=" * 50)
        print("\n操作說明：")
        print("  [Space]  暫停/繼續")
        print("  [S]      切換速度 (x1/x2/x4/x8)")
        print("  [R]      開始/停止錄影")
        print("  [N]      跳到下一代")
        print("  [ESC]    退出程式")
        print("\n開始模擬...\n")

        while self.is_running:
            # 處理事件
            self._handle_events()

            # 如果沒有暫停，更新模擬
            if not self.is_paused:
                dt = 1.0 / FPS

                # 根據速度倍率更新多次
                for _ in range(self.speed_multiplier):
                    self.current_time += dt
                    self._update_physics(dt)

                # 檢查這一代是否結束
                if self._check_generation_complete():
                    # 更新最佳適應度
                    current_best = max(c.fitness for c in self.creatures)
                    if current_best > self.best_fitness_ever:
                        self.best_fitness_ever = current_best

                    # 打印統計
                    avg_fitness = sum(c.fitness for c in self.creatures) / len(self.creatures)
                    stats = self.ga.get_statistics()
                    diversity = stats.get('current_diversity', 1.0)
                    mut_rate = stats.get('current_mutation_rate', MUTATION_RATE)

                    print(f"Generation {self.ga.generation + 1} complete: "
                          f"Best={current_best:.1f}, Avg={avg_fitness:.1f}, "
                          f"Diversity={diversity:.2f}, MutRate={mut_rate:.0%}")

                    # 初始化下一代
                    self._init_generation()

            # 渲染
            # 只顯示前 GRID_COUNT 隻生物
            display_creatures = self.creatures[:GRID_COUNT]
            current_best = max(c.fitness for c in self.creatures) if self.creatures else 0

            self.renderer.render(
                creatures=display_creatures,
                generation=self.ga.generation + 1,
                best_fitness=max(current_best, self.best_fitness_ever),
                current_time=self.current_time,
                is_paused=self.is_paused,
                is_recording=self.recorder.is_recording,
                speed_multiplier=self.speed_multiplier
            )

            # 錄影
            if self.recorder.is_recording:
                self.recorder.add_frame(self.screen)

            # 更新顯示
            pygame.display.flip()

            # 控制幀率
            self.clock.tick(FPS)

        # 清理
        self._cleanup()

    def _cleanup(self):
        """清理資源"""
        # 停止錄影
        if self.recorder.is_recording:
            self.recorder.stop_recording()

        # 清理生物
        self._cleanup_creatures()

        # 退出 Pygame
        pygame.quit()

        print("\n模擬結束！")
        print(f"總世代數：{self.ga.generation}")
        print(f"最佳距離：{self.best_fitness_ever:.1f}")


def main():
    """主函數"""
    try:
        sim = Simulation()
        sim.run()
    except KeyboardInterrupt:
        print("\n使用者中斷模擬")
    except Exception as e:
        print(f"錯誤：{e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
