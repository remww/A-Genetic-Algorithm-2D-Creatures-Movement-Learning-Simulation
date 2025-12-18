"""
步履蹣跚：基於物理引擎的 2D 生物行走演化
參數設定檔（第一階段改進版本）
"""

# ==================== 視窗設定 ====================
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
FPS = 60

# Grid 佈局 (2行 x 5列 = 10個格子)
GRID_ROWS = 2
GRID_COLS = 5
GRID_COUNT = GRID_ROWS * GRID_COLS

# 每個 Grid 的大小
CELL_WIDTH = WINDOW_WIDTH // GRID_COLS
CELL_HEIGHT = WINDOW_HEIGHT // GRID_ROWS

# ==================== 物理設定 ====================
GRAVITY = (0, -900)
PHYSICS_STEPS = 10

# 地面設定
GROUND_FRICTION = 1.0
GROUND_HEIGHT = 50

# ==================== 生物結構設定 ====================
TORSO_WIDTH = 60
TORSO_HEIGHT = 30
TORSO_MASS = 6

THIGH_LENGTH = 40
THIGH_WIDTH = 12
THIGH_MASS = 2

SHIN_LENGTH = 35
SHIN_WIDTH = 10
SHIN_MASS = 1.5

FOOT_WIDTH = 20
FOOT_HEIGHT = 5
FOOT_MASS = 0.5
FOOT_FRICTION = 2.0

BODY_FRICTION = 0.3

# ==================== 關節設定 ====================
MOTOR_MAX_FORCE = 800000

HIP_MIN_ANGLE = -0.8
HIP_MAX_ANGLE = 0.6
KNEE_MIN_ANGLE = 0.0
KNEE_MAX_ANGLE = 1.2

# ==================== 基因設定 ====================
GENES_PER_MOTOR = 3
MOTOR_COUNT = 4
GENE_COUNT = GENES_PER_MOTOR * MOTOR_COUNT

AMPLITUDE_MIN = 0.3
AMPLITUDE_MAX = 1.0
FREQUENCY_MIN = 0.5
FREQUENCY_MAX = 2.5
PHASE_MIN = 0.0
PHASE_MAX = 6.28318  # 2π

# ==================== 演化設定 ====================
POPULATION_SIZE = 50           # 增加到 50（更多多樣性）
SIMULATION_TIME = 15.0         # 縮短到 15 秒（加快迭代）
ELITE_RATIO = 0.1
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.15           # 降低到 15%
MUTATION_STRENGTH = 0.15       # 降低到 0.15

# ==================== 直立判定設定（新增）====================
# 直立高度閾值：軀幹高度必須高於此值才算直立
UPRIGHT_HEIGHT_THRESHOLD = 50
# 直立角度閾值：軀幹角度必須小於此值才算直立（約 20 度）
UPRIGHT_ANGLE_THRESHOLD = 0.35

# ==================== 適應度設定（改進版）====================
# 新公式：距離分數 = 直立時累積距離 × (高度比²) × (穩定性²)
FITNESS_DISTANCE_WEIGHT = 1.0      # 距離權重
FITNESS_UPRIGHT_WEIGHT = 1.0       # 直立時間獎勵權重（新增）
FITNESS_SURVIVAL_WEIGHT = 0.1      # 存活時間權重（降低）

# 懲罰設定
FITNESS_FALL_PENALTY = 200.0       # 摔倒懲罰（大幅提高！）
FITNESS_ENERGY_PENALTY = 0.01      # 能量懲罰（新增，防止抽搐）

# 預期站立高度
EXPECTED_STANDING_HEIGHT = THIGH_LENGTH + SHIN_LENGTH + FOOT_HEIGHT + TORSO_HEIGHT / 2

# ==================== 死亡條件 ====================
TORSO_TOUCH_GROUND_DEATH = True
TORSO_ANGLE_DEATH_THRESHOLD = 0.9
TORSO_HEIGHT_DEATH_THRESHOLD = 40

# ==================== 視角設定 ====================
CAMERA_SCROLL_DISTANCE = 200

# ==================== 顯示設定 ====================
COLOR_BACKGROUND = (30, 30, 40)
COLOR_GROUND = (80, 60, 40)
COLOR_TORSO = (70, 130, 180)
COLOR_THIGH = (100, 149, 237)
COLOR_SHIN = (135, 206, 235)
COLOR_FOOT = (255, 255, 255)
COLOR_JOINT = (255, 200, 100)
COLOR_TEXT = (255, 255, 255)
COLOR_GRID_LINE = (60, 60, 70)
COLOR_DEAD = (150, 50, 50)

# ==================== 錄影設定 ====================
RECORDING_FPS = 30
RECORDING_FILENAME = "evolution_recording.mp4"
