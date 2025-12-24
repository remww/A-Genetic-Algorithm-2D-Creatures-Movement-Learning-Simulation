import math
import random
import pymunk
from config import *


class Creature:
    def __init__(self, space: pymunk.Space, start_x: float, start_y: float, genes: list = None, creature_id: int = 0):
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

        # 適應度追蹤
        self.height_sum = 0.0
        self.stability_sum = 0.0
        self.update_count = 0
        self.upright_distance = 0.0
        self.last_x = start_x
        self.energy_used = 0.0
        self.upright_frames = 0
        # 踏步事件追蹤
        self.step_count = 0
        self._last_leg_delta_sign = {}

        # 身體部件字典 (用於渲染)
        self.named_parts = {}

        self._create_body()

    def _random_genes(self) -> list:
        genes = []
        for i in range(MOTOR_COUNT):
            genes.append(random.uniform(AMPLITUDE_MIN, AMPLITUDE_MAX))
            genes.append(random.uniform(FREQUENCY_MIN, FREQUENCY_MAX))
            genes.append(random.uniform(PHASE_MIN, PHASE_MAX))
        return genes

    def _create_box_body(self, x: float, y: float, width: float, height: float, mass: float, friction: float = BODY_FRICTION, group: int = 0) -> tuple:
        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = friction
        shape.filter = pymunk.ShapeFilter(group=group)  # 使用 group 防止同組碰撞
        
        # 身體碰撞類型
        shape.collision_type = 1

        self.space.add(body, shape)
        self.bodies.append(body)
        self.shapes.append(shape)

        return body, shape

    def _create_leg(self, hip_x: float, hip_y: float, group: int, motor_start_index: int, prefix: str):
        # 大腿
        thigh_y = hip_y - THIGH_LENGTH / 2
        thigh_body, thigh_shape = self._create_box_body(
            hip_x, thigh_y, THIGH_WIDTH, THIGH_LENGTH, THIGH_MASS, group=group
        )
        self.named_parts[f"{prefix}_thigh"] = (thigh_body, thigh_shape)

        # 小腿
        shin_y = thigh_y - THIGH_LENGTH / 2 - SHIN_LENGTH / 2
        shin_body, shin_shape = self._create_box_body(
            hip_x, shin_y, SHIN_WIDTH, SHIN_LENGTH, SHIN_MASS, group=group
        )
        self.named_parts[f"{prefix}_shin"] = (shin_body, shin_shape)

        # 腳
        foot_y = shin_y - SHIN_LENGTH / 2 - FOOT_HEIGHT / 2
        foot_body, foot_shape = self._create_box_body(
            hip_x, foot_y, FOOT_WIDTH, FOOT_HEIGHT, FOOT_MASS, FOOT_FRICTION, group=group
        )
        self.named_parts[f"{prefix}_foot"] = (foot_body, foot_shape)

        # 軀幹 -> 大腿 (髖關節)
        self._create_motor_joint(
            self.torso_body, thigh_body,
            (hip_x, hip_y), HIP_MIN_ANGLE, HIP_MAX_ANGLE, motor_index=motor_start_index
        )

        # 大腿 -> 小腿 (膝關節)
        self._create_motor_joint(
            thigh_body, shin_body,
            (hip_x, thigh_y - THIGH_LENGTH / 2), KNEE_MIN_ANGLE, KNEE_MAX_ANGLE, motor_index=motor_start_index + 1
        )

        # 小腿 -> 腳 (固定)
        self._create_fixed_joint(
            shin_body, foot_body, (hip_x, shin_y - SHIN_LENGTH / 2)
        )

    def _create_body(self):
        #根據設定選擇建立雙足或四足身體
        if CREATURE_TYPE == 'QUADRUPED':
            self._create_quadruped_body()
        else:
            self._create_biped_body()

    def _create_biped_body(self):
        x, y = self.start_x, self.start_y
        
        # 使用單一 collision group 避免自身碰撞
        unique_group = self.creature_id + 1

        # 軀幹
        torso_y = y + TORSO_HEIGHT / 2
        self.torso_body, self.torso_shape = self._create_box_body(
            x, torso_y, TORSO_WIDTH, TORSO_HEIGHT, TORSO_MASS, group=unique_group
        )
        self.torso_shape.collision_type = 2
        self.named_parts['torso'] = (self.torso_body, self.torso_shape)

        # 左腿
        left_hip_x = x - TORSO_WIDTH / 4
        hip_y = torso_y - TORSO_HEIGHT / 2
        self._create_leg(left_hip_x, hip_y, group=unique_group, motor_start_index=0, prefix="left")

        # 右腿
        right_hip_x = x + TORSO_WIDTH / 4
        self._create_leg(right_hip_x, hip_y, group=unique_group, motor_start_index=2, prefix="right")

    def _create_quadruped_body(self):
        x, y = self.start_x, self.start_y

        # 使用單一 collision group 避免自身碰撞
        unique_group = self.creature_id + 1

        # 軀幹
        torso_y = y + TORSO_HEIGHT / 2
        self.torso_body, self.torso_shape = self._create_box_body(
            x, torso_y, TORSO_WIDTH, TORSO_HEIGHT, TORSO_MASS, group=unique_group
        )
        self.torso_shape.collision_type = 2
        self.named_parts['torso'] = (self.torso_body, self.torso_shape)

        # 計算前後腿的髖關節位置
        offset_x = TORSO_WIDTH / 2 - 10 
        front_hip_x = x + offset_x
        back_hip_x = x - offset_x
        hip_y = torso_y - TORSO_HEIGHT / 2

        # 後腿
        # 所有腿使用相同的 unique_group，這樣它們重疊時不會產生爆炸性能量
        back_left_hip_x = back_hip_x - QUADRUPED_LEG_X_OFFSET
        back_right_hip_x = back_hip_x + QUADRUPED_LEG_X_OFFSET
        self._create_leg(back_left_hip_x, hip_y, group=unique_group, motor_start_index=0, prefix="back_left")
        self._create_leg(back_right_hip_x, hip_y, group=unique_group, motor_start_index=2, prefix="back_right")

        # 前腿
        front_left_hip_x = front_hip_x - QUADRUPED_LEG_X_OFFSET
        front_right_hip_x = front_hip_x + QUADRUPED_LEG_X_OFFSET
        self._create_leg(front_left_hip_x, hip_y, group=unique_group, motor_start_index=4, prefix="front_left")
        self._create_leg(front_right_hip_x, hip_y, group=unique_group, motor_start_index=6, prefix="front_right")


    def _create_motor_joint(self, body_a: pymunk.Body, body_b: pymunk.Body, anchor: tuple, min_angle: float, max_angle: float, motor_index: int):
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
        # 檢查是否處於直立狀態
        torso_height = self.torso_body.position.y
        torso_angle = abs(self.torso_body.angle)
        height_ok = torso_height > UPRIGHT_HEIGHT_THRESHOLD
        angle_ok = torso_angle < UPRIGHT_ANGLE_THRESHOLD

        return height_ok and angle_ok

    def _calculate_reflex_correction(self) -> tuple:
        # 計算反射修正量
        if not REFLEX_ENABLED:
            return 0.0, 0.0

        torso_angle = self.torso_body.angle
        torso_angular_velocity = self.torso_body.angular_velocity
        hip_correction = 0.0
        knee_correction = 0.0

        if abs(torso_angle) > REFLEX_BALANCE_THRESHOLD:
            hip_correction = -torso_angle * REFLEX_BALANCE_GAIN
            
            # 只有雙足模式下，才讓膝關節參與平衡反射
            if CREATURE_TYPE == 'BIPED':
                knee_correction = -torso_angle * REFLEX_BALANCE_GAIN * 0.3

        hip_correction -= torso_angular_velocity * REFLEX_VELOCITY_GAIN

        return hip_correction, knee_correction

    def _update_step_counter(self, dx: float, is_upright: bool):
        # 追蹤踏步事件：當一對腳的前後關係翻轉時，視為一次踏步。
        if CREATURE_TYPE == 'QUADRUPED':
            pairs = [
                ("front", "front_left_foot", "front_right_foot"),
                ("back", "back_left_foot", "back_right_foot"),
            ]
        else:
            pairs = [("biped", "left_foot", "right_foot")]

        for key, left_name, right_name in pairs:
            left_part = self.named_parts.get(left_name)
            right_part = self.named_parts.get(right_name)
            if not left_part or not right_part:
                continue

            left_body, _ = left_part
            right_body, _ = right_part

            leg_delta = right_body.position.x - left_body.position.x
            if abs(leg_delta) < STEP_MIN_LEG_DELTA:
                continue

            sign = 1 if leg_delta > 0 else -1
            last_sign = self._last_leg_delta_sign.get(key)
            self._last_leg_delta_sign[key] = sign

            if last_sign is None:
                continue

            if sign != last_sign and is_upright and dx > 0:
                self.step_count += 1

    def update(self, dt: float, current_time: float):
        if not self.is_alive:
            return

        self.time_alive += dt
        self.update_count += 1

        hip_correction, knee_correction = self._calculate_reflex_correction()
        shared_freq = self.genes[1] if SHARED_FREQUENCY else 0.0
        
        frame_energy = 0.0

        for i, motor in enumerate(self.motors):
            gene_base = i * GENES_PER_MOTOR
            amplitude = self.genes[gene_base]
            
            if SHARED_FREQUENCY:
                frequency = shared_freq
            else:
                frequency = self.genes[gene_base + 1]
                
            phase = self.genes[gene_base + 2]

            target_rate = amplitude * frequency * math.cos(frequency * current_time * 2 * math.pi + phase)

            # 判斷是否為髖關節
            is_hip = False
            if CREATURE_TYPE == 'QUADRUPED':
                 # 四足: 0, 2, 4, 6 是髖
                 if i % 2 == 0:
                     is_hip = True
            else:
                 # 雙足: 0, 2 是髖
                 if i in [0, 2]:
                     is_hip = True

            if is_hip:
                target_rate += hip_correction
            else:
                target_rate += knee_correction

            motor.rate = target_rate * 3
            frame_energy += abs(motor.rate)

        self.energy_used += frame_energy

        # 追蹤軀幹高度
        torso_height = self.torso_body.position.y
        self.height_sum += torso_height

        # 追蹤穩定性
        torso_angle = abs(self.torso_body.angle)
        stability = max(0, 1.0 - torso_angle / (math.pi / 2))
        self.stability_sum += stability

        # 只在直立時累積距離
        current_x = self.torso_body.position.x
        dx = current_x - self.last_x

        is_upright = self._is_upright()
        if is_upright:
            self.upright_frames += 1
            if dx > 0:
                self.upright_distance += dx

        self._update_step_counter(dx, is_upright)

        self.last_x = current_x

        self._calculate_fitness()


    def _calculate_fitness(self):
        # 計算綜合適應度
        
        # 距離分數（核心）
        distance_score = self.upright_distance * FITNESS_DISTANCE_WEIGHT
        
        # 直立時間獎勵（輔助）
        upright_score = self.upright_frames * 0.1 * FITNESS_UPRIGHT_WEIGHT

        # 踏步事件獎勵
        step_score = self.step_count * FITNESS_STEP_REWARD

        # 摔倒懲罰
        fall_penalty = FITNESS_FALL_PENALTY if self.fell_down else 0.0
        
        # 能量懲罰
        energy_penalty = 0.0
        if FITNESS_ENERGY_PENALTY > 0 and self.update_count > 0:
            avg_energy = self.energy_used / self.update_count
            energy_penalty = avg_energy * FITNESS_ENERGY_PENALTY

        # 總分
        self.fitness = distance_score + upright_score + step_score - fall_penalty - energy_penalty
        
        # 確保分數不為負
        if self.fitness < 0:
            self.fitness = 0.0

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
        return self.named_parts