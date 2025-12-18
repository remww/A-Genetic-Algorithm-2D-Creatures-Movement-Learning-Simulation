"""
步履蹣跚：基於物理引擎的 2D 生物行走演化
生物類別 - 包含身體結構、基因和馬達控制
"""

import math
import random
import pymunk
from config import *


class Creature:
    """
    生物類別

    身體結構：
        [軀幹 Torso]
         /        \
    [左大腿]     [右大腿]
       |           |
    [左小腿]     [右小腿]
       |           |
     (左腳)      (右腳)

    4 個馬達：
    - 馬達 0：左髖關節（軀幹 ↔ 左大腿）
    - 馬達 1：左膝關節（左大腿 ↔ 左小腿）
    - 馬達 2：右髖關節（軀幹 ↔ 右大腿）
    - 馬達 3：右膝關節（右大腿 ↔ 右小腿）
    """

    def __init__(self, space: pymunk.Space, start_x: float, start_y: float,
                 genes: list = None, creature_id: int = 0):
        """
        初始化生物

        Args:
            space: Pymunk 物理空間
            start_x: 起始 X 座標
            start_y: 起始 Y 座標（軀幹底部）
            genes: 基因列表，如果為 None 則隨機生成
            creature_id: 生物 ID（用於識別）
        """
        self.space = space
        self.start_x = start_x
        self.start_y = start_y
        self.creature_id = creature_id

        # 初始化基因（如果未提供則隨機生成）
        self.genes = genes if genes is not None else self._random_genes()

        # 身體部件
        self.bodies = []
        self.shapes = []
        self.motors = []
        self.pivot_joints = []
        self.rotary_limit_joints = []

        # 狀態
        self.is_alive = True
        self.time_alive = 0.0
        self.fitness = 0.0
        self.fell_down = False  # 是否摔倒

        # 適應度追蹤（用於計算平均值）
        self.height_sum = 0.0        # 累積軀幹高度
        self.stability_sum = 0.0     # 累積穩定性（角度接近0的程度）
        self.update_count = 0        # 更新次數

        # 建立身體
        self._create_body()

    def _random_genes(self) -> list:
        """生成隨機基因"""
        genes = []
        for i in range(MOTOR_COUNT):
            # 振幅 A
            genes.append(random.uniform(AMPLITUDE_MIN, AMPLITUDE_MAX))
            # 頻率 ω
            genes.append(random.uniform(FREQUENCY_MIN, FREQUENCY_MAX))
            # 相位 φ
            genes.append(random.uniform(PHASE_MIN, PHASE_MAX))
        return genes

    def _create_box_body(self, x: float, y: float, width: float, height: float,
                         mass: float, friction: float = BODY_FRICTION) -> tuple:
        """
        創建矩形物理體

        Returns:
            (body, shape) 元組
        """
        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = friction
        shape.collision_type = 1  # 用於碰撞檢測

        self.space.add(body, shape)
        self.bodies.append(body)
        self.shapes.append(shape)

        return body, shape

    def _create_body(self):
        """建立完整的身體結構"""
        x, y = self.start_x, self.start_y

        # ==================== 軀幹 ====================
        torso_y = y + TORSO_HEIGHT / 2
        self.torso_body, self.torso_shape = self._create_box_body(
            x, torso_y, TORSO_WIDTH, TORSO_HEIGHT, TORSO_MASS
        )
        self.torso_shape.collision_type = 2  # 軀幹特殊碰撞類型

        # ==================== 左腿 ====================
        # 左大腿
        left_hip_x = x - TORSO_WIDTH / 4
        left_thigh_y = torso_y - TORSO_HEIGHT / 2 - THIGH_LENGTH / 2
        self.left_thigh_body, self.left_thigh_shape = self._create_box_body(
            left_hip_x, left_thigh_y, THIGH_WIDTH, THIGH_LENGTH, THIGH_MASS
        )

        # 左小腿
        left_shin_y = left_thigh_y - THIGH_LENGTH / 2 - SHIN_LENGTH / 2
        self.left_shin_body, self.left_shin_shape = self._create_box_body(
            left_hip_x, left_shin_y, SHIN_WIDTH, SHIN_LENGTH, SHIN_MASS
        )

        # 左腳
        left_foot_y = left_shin_y - SHIN_LENGTH / 2 - FOOT_HEIGHT / 2
        self.left_foot_body, self.left_foot_shape = self._create_box_body(
            left_hip_x, left_foot_y, FOOT_WIDTH, FOOT_HEIGHT, FOOT_MASS, FOOT_FRICTION
        )

        # ==================== 右腿 ====================
        # 右大腿
        right_hip_x = x + TORSO_WIDTH / 4
        right_thigh_y = torso_y - TORSO_HEIGHT / 2 - THIGH_LENGTH / 2
        self.right_thigh_body, self.right_thigh_shape = self._create_box_body(
            right_hip_x, right_thigh_y, THIGH_WIDTH, THIGH_LENGTH, THIGH_MASS
        )

        # 右小腿
        right_shin_y = right_thigh_y - THIGH_LENGTH / 2 - SHIN_LENGTH / 2
        self.right_shin_body, self.right_shin_shape = self._create_box_body(
            right_hip_x, right_shin_y, SHIN_WIDTH, SHIN_LENGTH, SHIN_MASS
        )

        # 右腳
        right_foot_y = right_shin_y - SHIN_LENGTH / 2 - FOOT_HEIGHT / 2
        self.right_foot_body, self.right_foot_shape = self._create_box_body(
            right_hip_x, right_foot_y, FOOT_WIDTH, FOOT_HEIGHT, FOOT_MASS, FOOT_FRICTION
        )

        # ==================== 關節連接 ====================
        # 左髖關節（軀幹 ↔ 左大腿）
        left_hip_anchor = (left_hip_x, torso_y - TORSO_HEIGHT / 2)
        self._create_motor_joint(
            self.torso_body, self.left_thigh_body,
            left_hip_anchor,
            HIP_MIN_ANGLE, HIP_MAX_ANGLE,
            motor_index=0
        )

        # 左膝關節（左大腿 ↔ 左小腿）
        left_knee_anchor = (left_hip_x, left_thigh_y - THIGH_LENGTH / 2)
        self._create_motor_joint(
            self.left_thigh_body, self.left_shin_body,
            left_knee_anchor,
            KNEE_MIN_ANGLE, KNEE_MAX_ANGLE,
            motor_index=1
        )

        # 左踝關節（左小腿 ↔ 左腳）- 固定連接，無馬達
        left_ankle_anchor = (left_hip_x, left_shin_y - SHIN_LENGTH / 2)
        self._create_fixed_joint(self.left_shin_body, self.left_foot_body, left_ankle_anchor)

        # 右髖關節（軀幹 ↔ 右大腿）
        right_hip_anchor = (right_hip_x, torso_y - TORSO_HEIGHT / 2)
        self._create_motor_joint(
            self.torso_body, self.right_thigh_body,
            right_hip_anchor,
            HIP_MIN_ANGLE, HIP_MAX_ANGLE,
            motor_index=2
        )

        # 右膝關節（右大腿 ↔ 右小腿）
        right_knee_anchor = (right_hip_x, right_thigh_y - THIGH_LENGTH / 2)
        self._create_motor_joint(
            self.right_thigh_body, self.right_shin_body,
            right_knee_anchor,
            KNEE_MIN_ANGLE, KNEE_MAX_ANGLE,
            motor_index=3
        )

        # 右踝關節（右小腿 ↔ 右腳）- 固定連接，無馬達
        right_ankle_anchor = (right_hip_x, right_shin_y - SHIN_LENGTH / 2)
        self._create_fixed_joint(self.right_shin_body, self.right_foot_body, right_ankle_anchor)

    def _create_motor_joint(self, body_a: pymunk.Body, body_b: pymunk.Body,
                            anchor: tuple, min_angle: float, max_angle: float,
                            motor_index: int):
        """
        創建帶馬達的關節

        Args:
            body_a: 第一個物體
            body_b: 第二個物體
            anchor: 關節錨點（世界座標）
            min_angle: 最小角度
            max_angle: 最大角度
            motor_index: 馬達索引
        """
        # PivotJoint - 讓兩個物體可以繞著錨點旋轉
        pivot = pymunk.PivotJoint(body_a, body_b, anchor)
        pivot.collide_bodies = False  # 連接的物體不互相碰撞
        self.space.add(pivot)
        self.pivot_joints.append(pivot)

        # RotaryLimitJoint - 限制旋轉角度
        rotary_limit = pymunk.RotaryLimitJoint(body_a, body_b, min_angle, max_angle)
        self.space.add(rotary_limit)
        self.rotary_limit_joints.append(rotary_limit)

        # SimpleMotor - 提供旋轉動力
        motor = pymunk.SimpleMotor(body_a, body_b, 0)  # 初始速度為 0
        motor.max_force = MOTOR_MAX_FORCE
        self.space.add(motor)
        self.motors.append(motor)

    def _create_fixed_joint(self, body_a: pymunk.Body, body_b: pymunk.Body, anchor: tuple):
        """創建固定連接（踝關節）"""
        pivot = pymunk.PivotJoint(body_a, body_b, anchor)
        pivot.collide_bodies = False
        self.space.add(pivot)
        self.pivot_joints.append(pivot)

        # 添加 GearJoint 使兩個物體保持相同角度
        gear = pymunk.GearJoint(body_a, body_b, 0, 1)
        self.space.add(gear)

    def update(self, dt: float, current_time: float):
        """
        更新生物狀態

        Args:
            dt: 時間步長
            current_time: 當前模擬時間
        """
        if not self.is_alive:
            return

        self.time_alive += dt
        self.update_count += 1

        # 更新馬達速度（根據正弦波）
        for i, motor in enumerate(self.motors):
            # 從基因獲取參數
            gene_base = i * GENES_PER_MOTOR
            amplitude = self.genes[gene_base]      # A
            frequency = self.genes[gene_base + 1]  # ω
            phase = self.genes[gene_base + 2]      # φ

            # θ(t) = A × sin(ω × t + φ)
            # 馬達速度 = dθ/dt = A × ω × cos(ω × t + φ)
            target_rate = amplitude * frequency * math.cos(frequency * current_time * 2 * math.pi + phase)
            motor.rate = target_rate * 3  # 放大係數提高到 3

        # 追蹤軀幹高度（用於計算平均高度獎勵）
        torso_height = self.torso_body.position.y
        self.height_sum += torso_height

        # 追蹤穩定性（軀幹角度接近 0 的程度）
        # 角度為 0 時穩定性為 1，角度越大穩定性越低
        torso_angle = abs(self.torso_body.angle)
        stability = max(0, 1.0 - torso_angle / (math.pi / 2))  # 傾斜 90 度時穩定性為 0
        self.stability_sum += stability

        # 計算綜合適應度
        self._calculate_fitness()

    def _calculate_fitness(self):
        """計算綜合適應度"""
        # 1. 距離獎勵（主要因素）
        distance = self.torso_body.position.x - self.start_x
        distance_score = distance * FITNESS_DISTANCE_WEIGHT

        # 2. 平均高度獎勵（鼓勵站立）
        if self.update_count > 0:
            avg_height = self.height_sum / self.update_count
            # 高度獎勵：越接近預期站立高度越好
            height_ratio = min(1.0, avg_height / EXPECTED_STANDING_HEIGHT)
            height_score = height_ratio * 100 * FITNESS_HEIGHT_WEIGHT
        else:
            height_score = 0

        # 3. 平均穩定性獎勵（鼓勵保持直立）
        if self.update_count > 0:
            avg_stability = self.stability_sum / self.update_count
            stability_score = avg_stability * 100 * FITNESS_STABILITY_WEIGHT
        else:
            stability_score = 0

        # 4. 存活時間獎勵
        survival_score = self.time_alive * 10 * FITNESS_SURVIVAL_WEIGHT

        # 5. 摔倒懲罰
        fall_penalty = FITNESS_FALL_PENALTY if self.fell_down else 0

        # 綜合適應度
        self.fitness = distance_score + height_score + stability_score + survival_score - fall_penalty

    def check_death(self, ground_y: float) -> bool:
        """
        檢查是否死亡

        Args:
            ground_y: 地面 Y 座標

        Returns:
            是否死亡
        """
        if not self.is_alive:
            return True

        # 檢查時間限制
        if self.time_alive >= SIMULATION_TIME:
            self.is_alive = False
            self._calculate_fitness()  # 最終計算適應度
            return True

        # 檢查軀幹是否觸地
        if TORSO_TOUCH_GROUND_DEATH:
            torso_bottom = self.torso_body.position.y - TORSO_HEIGHT / 2
            if torso_bottom <= ground_y + 5:  # 5 pixels 容差
                self.is_alive = False
                self.fell_down = True  # 標記為摔倒
                self._calculate_fitness()  # 最終計算適應度
                return True

        # 檢查軀幹是否過度傾斜（側躺）
        torso_angle = abs(self.torso_body.angle)
        if torso_angle > TORSO_ANGLE_DEATH_THRESHOLD:
            self.is_alive = False
            self.fell_down = True
            self._calculate_fitness()
            return True

        # 檢查軀幹高度是否過低（趴在地上）
        torso_height = self.torso_body.position.y
        if torso_height < TORSO_HEIGHT_DEATH_THRESHOLD:
            self.is_alive = False
            self.fell_down = True
            self._calculate_fitness()
            return True

        return False

    def get_position(self) -> tuple:
        """獲取軀幹位置"""
        return self.torso_body.position.x, self.torso_body.position.y

    def remove_from_space(self):
        """從物理空間中移除所有物體"""
        # 移除馬達
        for motor in self.motors:
            if motor in self.space.constraints:
                self.space.remove(motor)

        # 移除關節
        for joint in self.pivot_joints:
            if joint in self.space.constraints:
                self.space.remove(joint)

        for joint in self.rotary_limit_joints:
            if joint in self.space.constraints:
                self.space.remove(joint)

        # 移除形狀和物體
        for shape in self.shapes:
            if shape in self.space.shapes:
                self.space.remove(shape)

        for body in self.bodies:
            if body in self.space.bodies:
                self.space.remove(body)

        # 清空列表
        self.motors.clear()
        self.pivot_joints.clear()
        self.rotary_limit_joints.clear()
        self.shapes.clear()
        self.bodies.clear()

    def get_all_bodies(self) -> list:
        """獲取所有身體部件"""
        return self.bodies

    def get_body_info(self) -> dict:
        """獲取身體資訊（用於渲染）"""
        return {
            'torso': (self.torso_body, self.torso_shape),
            'left_thigh': (self.left_thigh_body, self.left_thigh_shape),
            'left_shin': (self.left_shin_body, self.left_shin_shape),
            'left_foot': (self.left_foot_body, self.left_foot_shape),
            'right_thigh': (self.right_thigh_body, self.right_thigh_shape),
            'right_shin': (self.right_shin_body, self.right_shin_shape),
            'right_foot': (self.right_foot_body, self.right_foot_shape),
        }
