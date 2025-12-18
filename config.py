"""
步履蹣跚：基於物理引擎的 2D 生物行走演化
參數設定檔
"""

# ==================== 視窗設定 ====================
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
FPS = 60

# Grid 佈局 (2行 x 5列 = 10個格子)
GRID_ROWS = 2
GRID_COLS = 5
GRID_COUNT = GRID_ROWS * GRID_COLS  # 同時顯示 10 隻生物

# 每個 Grid 的大小
CELL_WIDTH = WINDOW_WIDTH // GRID_COLS   # 320
CELL_HEIGHT = WINDOW_HEIGHT // GRID_ROWS  # 450

# ==================== 物理設定 ====================
GRAVITY = (0, -900)  # 向下的重力（Pymunk Y軸向上，所以用負數）
PHYSICS_STEPS = 10  # 每幀物理步數（提高穩定性）

# 地面設定
GROUND_FRICTION = 1.0
GROUND_HEIGHT = 50  # 地面距離 cell 底部的高度

# ==================== 生物結構設定 ====================
# 軀幹
TORSO_WIDTH = 60
TORSO_HEIGHT = 30
TORSO_MASS = 6  # 稍微降低，讓動作更靈活

# 大腿
THIGH_LENGTH = 40
THIGH_WIDTH = 12
THIGH_MASS = 2

# 小腿
SHIN_LENGTH = 35
SHIN_WIDTH = 10
SHIN_MASS = 1.5

# 腳掌（用於增加摩擦力）
FOOT_WIDTH = 20
FOOT_HEIGHT = 5
FOOT_MASS = 0.5
FOOT_FRICTION = 2.0

# 身體各部位摩擦力
BODY_FRICTION = 0.3

# ==================== 關節設定 ====================
# 馬達最大力矩（提高讓動作更有力）
MOTOR_MAX_FORCE = 800000  # 提高到 800000

# 關節角度限制（弧度）
HIP_MIN_ANGLE = -0.8
HIP_MAX_ANGLE = 0.6
KNEE_MIN_ANGLE = 0.0
KNEE_MAX_ANGLE = 1.2

# ==================== 基因設定 ====================
# 每個馬達有 3 個參數：振幅(A)、頻率(ω)、相位(φ)
# 總共 4 個馬達 = 12 個基因
GENES_PER_MOTOR = 3
MOTOR_COUNT = 4
GENE_COUNT = GENES_PER_MOTOR * MOTOR_COUNT  # 12

# 基因範圍（提高頻率和振幅，讓動作更快）
AMPLITUDE_MIN = 0.3
AMPLITUDE_MAX = 1.0
FREQUENCY_MIN = 0.5    # 提高最低頻率
FREQUENCY_MAX = 2.5    # 提高最高頻率
PHASE_MIN = 0.0
PHASE_MAX = 6.28       # 2π

# ==================== 演化設定 ====================
POPULATION_SIZE = 30
SIMULATION_TIME = 20.0     # 降到 20 秒（加快每代速度）
ELITE_RATIO = 0.1          # 降低菁英比例（更高選擇壓力）
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.2        # 提高突變率（加快探索）
MUTATION_STRENGTH = 0.25   # 提高突變強度

# ==================== 適應度設定 ====================
# 適應度 = 距離權重 × 距離 + 高度權重 × 平均高度 + 穩定權重 × 穩定分數 - 摔倒懲罰
FITNESS_DISTANCE_WEIGHT = 1.0      # 距離權重（主要）
FITNESS_HEIGHT_WEIGHT = 0.3        # 降低高度權重
FITNESS_STABILITY_WEIGHT = 0.2     # 降低穩定性權重
FITNESS_SURVIVAL_WEIGHT = 0.1      # 降低存活權重
FITNESS_FALL_PENALTY = 30.0        # 降低摔倒懲罰

# 預期站立高度（用於計算高度獎勵）
EXPECTED_STANDING_HEIGHT = THIGH_LENGTH + SHIN_LENGTH + FOOT_HEIGHT + TORSO_HEIGHT / 2

# ==================== 死亡條件 ====================
# 軀幹接觸地面即為摔倒
TORSO_TOUCH_GROUND_DEATH = True
# 軀幹傾斜超過此角度（弧度）視為摔倒（約 52 度）
TORSO_ANGLE_DEATH_THRESHOLD = 0.9
# 軀幹高度低於此值視為摔倒
TORSO_HEIGHT_DEATH_THRESHOLD = 40

# ==================== 視角設定 ====================
# 當生物超出視角右邊界時，視角向右移動的距離
CAMERA_SCROLL_DISTANCE = 200  # pixels

# ==================== 顯示設定 ====================
# 顏色定義 (RGB)
COLOR_BACKGROUND = (30, 30, 40)
COLOR_GROUND = (80, 60, 40)
COLOR_TORSO = (70, 130, 180)      # 軀幹 - 鋼藍色
COLOR_THIGH = (100, 149, 237)     # 大腿 - 矢車菊藍
COLOR_SHIN = (135, 206, 235)      # 小腿 - 天藍色
COLOR_FOOT = (255, 255, 255)      # 腳掌 - 白色
COLOR_JOINT = (255, 200, 100)     # 關節 - 橙黃色
COLOR_TEXT = (255, 255, 255)      # 文字 - 白色
COLOR_GRID_LINE = (60, 60, 70)    # Grid 分隔線
COLOR_DEAD = (150, 50, 50)        # 死亡生物的顏色

# ==================== 錄影設定 ====================
RECORDING_FPS = 30
RECORDING_FILENAME = "evolution_recording.mp4"
