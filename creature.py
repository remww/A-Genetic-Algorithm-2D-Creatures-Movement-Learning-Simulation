"""
步履蹣跚：基於物理引擎的 2D 生物行走演化
生物類別 - 包含身體結構、基因和馬達控制
（第一階段改進版本）
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
        self.space = space
        self.start_x = start_x
        self.start_y = start_y
        self.creature_id = creature_id

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
        self.fell_down = False

        # 適應度追蹤（改進版）
        self.height_sum = 0.0
        self.stability_sum = 0.0
        self.update_count = 0

        # 新增：只在直立時累積的距離
        self.upright_distance = 0.0
        self.last_x = start_x

        # 新增：能量消耗追蹤
        self.energy_used = 0.0

        # 新增：直立時間計數
        self.upright_frames = 0

        self._create_body()

    def _random_genes(self) -> list:
        genes = []
        for i in range(MOTOR_COUNT):
            genes.append(random.uniform(AMPLITUDE_MIN, AMPLITUDE_MAX))
            genes.append(random.uniform(FREQUENCY_MIN, FREQUENCY_MAX))
            genes.append(random.uniform(PHASE_MIN, PHASE_MAX))
        return genes

    def _create_box_body(self, x: float, y: float, width: float, height: float,
                         mass: float, friction: float = BODY_FRICTION) -> tuple:
        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = friction
        shape.collision_type = 1

        self.space.add(body, shape)
        self.bodies.append(body)
        self.shapes.append(shape)

        return body, shape

    def _create_body(self):
        x, y = self.start_x, self.start_y

        # 軀幹
        torso_y = y + TORSO_HEIGHT / 2
        self.torso_body, self.torso_shape = self._create_box_body(
            x, torso_y, TORSO_WIDTH, TORSO_HEIGHT, TORSO_MASS
        )
        self.torso_shape.collision_type = 2

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

        # 關節連接
        left_hip_anchor = (left_hip_x, torso_y - TORSO_HEIGHT / 2)
        self._create_motor_joint(
            self.torso_body, self.left_thigh_body,
            left_hip_anchor, HIP_MIN_ANGLE, HIP_MAX_ANGLE, motor_index=0
        )

        left_knee_anchor = (left_hip_x, left_thigh_y - THIGH_LENGTH / 2)
        self._create_motor_joint(
            self.left_thigh_body, self.left_shin_body,
            left_knee_anchor, KNEE_MIN_ANGLE, KNEE_MAX_ANGLE, motor_index=1
        )

        left_ankle_anchor = (left_hip_x, left_shin_y - SHIN_LENGTH / 2)
        self._create_fixed_joint(self.left_shin_body, self.left_foot_body, left_ankle_anchor)

        right_hip_anchor = (right_hip_x, torso_y - TORSO_HEIGHT / 2)
        self._create_motor_joint(
            self.torso_body, self.right_thigh_body,
            right_hip_anchor, HIP_MIN_ANGLE, HIP_MAX_ANGLE, motor_index=2
        )

        right_knee_anchor = (right_hip_x, right_thigh_y - THIGH_LENGTH / 2)
        self._create_motor_joint(
            self.right_thigh_body, self.right_shin_body,
            right_knee_anchor, KNEE_MIN_ANGLE, KNEE_MAX_ANGLE, motor_index=3
        )

        right_ankle_anchor = (right_hip_x, right_shin_y - SHIN_LENGTH / 2)
        self._create_fixed_joint(self.right_shin_body, self.right_foot_body, right_ankle_anchor)

    def _create_motor_joint(self, body_a: pymunk.Body, body_b: pymunk.Body,
                            anchor: tuple, min_angle: float, max_angle: float,
                            motor_index: int):
        pivot = pymunk.PivotJoint(body_a, body_b, anchor)
        pivot.collide_bodies = False
        self.space.add(pivot)
        self.pivot_joints.append(pivot)

        rotary_limit = pymunk.RotaryLimitJoint(body_a, body_b, min_angle, max_angle)
        self.space.add(rotary_limit)
        self.rotary_limit_joints.append(rotary_limit)

        motor = pymunk.SimpleMotor(body_a, body_b, 0)
        motor.max_force = MOTOR_MAX_FORCE
        self.space.add(motor)
        self.motors.append(motor)

    def _create_fixed_joint(self, body_a: pymunk.Body, body_b: pymunk.Body, anchor: tuple):
        pivot = pymunk.PivotJoint(body_a, body_b, anchor)
        pivot.collide_bodies = False
        self.space.add(pivot)
        self.pivot_joints.append(pivot)

        gear = pymunk.GearJoint(body_a, body_b, 0, 1)
        self.space.add(gear)

    def _is_upright(self) -> bool:
        """檢查是否處於直立狀態"""
        torso_height = self.torso_body.position.y
        torso_angle = abs(self.torso_body.angle)

        # 直立條件：高度足夠且角度小
        height_ok = torso_height > UPRIGHT_HEIGHT_THRESHOLD
        angle_ok = torso_angle < UPRIGHT_ANGLE_THRESHOLD

        return height_ok and angle_ok

    def update(self, dt: float, current_time: float):
        if not self.is_alive:
            return

        self.time_alive += dt
        self.update_count += 1

        # 更新馬達速度並累積能量消耗
        frame_energy = 0.0
        for i, motor in enumerate(self.motors):
            gene_base = i * GENES_PER_MOTOR
            amplitude = self.genes[gene_base]
            frequency = self.genes[gene_base + 1]
            phase = self.genes[gene_base + 2]

            target_rate = amplitude * frequency * math.cos(frequency * current_time * 2 * math.pi + phase)
            motor.rate = target_rate * 3

            # 累積能量消耗（馬達速度的絕對值）
            frame_energy += abs(motor.rate)

        self.energy_used += frame_energy

        # 追蹤軀幹高度
        torso_height = self.torso_body.position.y
        self.height_sum += torso_height

        # 追蹤穩定性
        torso_angle = abs(self.torso_body.angle)
        stability = max(0, 1.0 - torso_angle / (math.pi / 2))
        self.stability_sum += stability

        # 【改進】只在直立時累積距離
        current_x = self.torso_body.position.x
        dx = current_x - self.last_x

        if self._is_upright():
            self.upright_frames += 1
            # 只累積正向（往右）的距離
            if dx > 0:
                self.upright_distance += dx

        self.last_x = current_x

        self._calculate_fitness()

    def _calculate_fitness(self):
        """計算綜合適應度（改進版：乘法綁定 + 能量懲罰）"""

        # 計算基礎指標
        if self.update_count > 0:
            avg_height = self.height_sum / self.update_count
            height_ratio = min(1.0, max(0, avg_height / EXPECTED_STANDING_HEIGHT))

            avg_stability = self.stability_sum / self.update_count

            upright_ratio = self.upright_frames / self.update_count
        else:
            height_ratio = 0
            avg_stability = 0
            upright_ratio = 0

        # 【改進】乘法綁定：距離分數 × 直立指標
        # 這樣「往前倒」就拿不到分了
        base_distance = max(0, self.upright_distance)

        # 綜合直立係數（高度 × 穩定性）
        upright_multiplier = (height_ratio ** 2) * (avg_stability ** 2)

        # 距離分數 = 直立時累積的距離 × 直立係數
        distance_score = base_distance * upright_multiplier * FITNESS_DISTANCE_WEIGHT

        # 直立時間獎勵
        upright_bonus = upright_ratio * 50 * FITNESS_UPRIGHT_WEIGHT

        # 存活時間獎勵（降低權重）
        survival_score = self.time_alive * 5 * FITNESS_SURVIVAL_WEIGHT

        # 【新增】能量懲罰（防止抽搐）
        if self.update_count > 0:
            avg_energy = self.energy_used / self.update_count
            energy_penalty = avg_energy * FITNESS_ENERGY_PENALTY
        else:
            energy_penalty = 0

        # 摔倒懲罰（大幅提高）
        fall_penalty = FITNESS_FALL_PENALTY if self.fell_down else 0

        # 綜合適應度
        self.fitness = distance_score + upright_bonus + survival_score - energy_penalty - fall_penalty

    def check_death(self, ground_y: float) -> bool:
        if not self.is_alive:
            return True

        if self.time_alive >= SIMULATION_TIME:
            self.is_alive = False
            self._calculate_fitness()
            return True

        if TORSO_TOUCH_GROUND_DEATH:
            torso_bottom = self.torso_body.position.y - TORSO_HEIGHT / 2
            if torso_bottom <= ground_y + 5:
                self.is_alive = False
                self.fell_down = True
                self._calculate_fitness()
                return True

        torso_angle = abs(self.torso_body.angle)
        if torso_angle > TORSO_ANGLE_DEATH_THRESHOLD:
            self.is_alive = False
            self.fell_down = True
            self._calculate_fitness()
            return True

        torso_height = self.torso_body.position.y
        if torso_height < TORSO_HEIGHT_DEATH_THRESHOLD:
            self.is_alive = False
            self.fell_down = True
            self._calculate_fitness()
            return True

        return False

    def get_position(self) -> tuple:
        return self.torso_body.position.x, self.torso_body.position.y

    def remove_from_space(self):
        for motor in self.motors:
            if motor in self.space.constraints:
                self.space.remove(motor)

        for joint in self.pivot_joints:
            if joint in self.space.constraints:
                self.space.remove(joint)

        for joint in self.rotary_limit_joints:
            if joint in self.space.constraints:
                self.space.remove(joint)

        for shape in self.shapes:
            if shape in self.space.shapes:
                self.space.remove(shape)

        for body in self.bodies:
            if body in self.space.bodies:
                self.space.remove(body)

        self.motors.clear()
        self.pivot_joints.clear()
        self.rotary_limit_joints.clear()
        self.shapes.clear()
        self.bodies.clear()

    def get_all_bodies(self) -> list:
        return self.bodies

    def get_body_info(self) -> dict:
        return {
            'torso': (self.torso_body, self.torso_shape),
            'left_thigh': (self.left_thigh_body, self.left_thigh_shape),
            'left_shin': (self.left_shin_body, self.left_shin_shape),
            'left_foot': (self.left_foot_body, self.left_foot_shape),
            'right_thigh': (self.right_thigh_body, self.right_thigh_shape),
            'right_shin': (self.right_shin_body, self.right_shin_shape),
            'right_foot': (self.right_foot_body, self.right_foot_shape),
        }
