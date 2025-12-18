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
TORSO_MASS = 5

# 大腿
THIGH_LENGTH = 40
THIGH_WIDTH = 12
THIGH_MASS = 2

# 小腿
SHIN_LENGTH = 35
SHIN_WIDTH = 10
SHIN_MASS = 1.5

# 腳掌（用於增加摩擦力）
FOOT_WIDTH = 15
FOOT_HEIGHT = 5
FOOT_MASS = 0.5
FOOT_FRICTION = 1.5

# 身體各部位摩擦力
BODY_FRICTION = 0.3

# ==================== 關節設定 ====================
# 馬達最大力矩
MOTOR_MAX_FORCE = 5000000

# 關節角度限制（弧度）
HIP_MIN_ANGLE = -1.2   # 髖關節最小角度
HIP_MAX_ANGLE = 0.8    # 髖關節最大角度
KNEE_MIN_ANGLE = -0.1  # 膝關節最小角度
KNEE_MAX_ANGLE = 1.5   # 膝關節最大角度

# ==================== 基因設定 ====================
# 每個馬達有 3 個參數：振幅(A)、頻率(ω)、相位(φ)
# 總共 4 個馬達 = 12 個基因
GENES_PER_MOTOR = 3
MOTOR_COUNT = 4
GENE_COUNT = GENES_PER_MOTOR * MOTOR_COUNT  # 12

# 基因範圍
AMPLITUDE_MIN = 0.3    # 振幅最小值
AMPLITUDE_MAX = 1.2    # 振幅最大值
FREQUENCY_MIN = 1.0    # 頻率最小值 (Hz)
FREQUENCY_MAX = 4.0    # 頻率最大值 (Hz)
PHASE_MIN = 0.0        # 相位最小值
PHASE_MAX = 6.28       # 相位最大值 (2π)

# ==================== 演化設定 ====================
POPULATION_SIZE = 20       # 族群大小（每代 20 隻）
SIMULATION_TIME = 10.0     # 每隻生物的模擬時間（秒）
ELITE_RATIO = 0.2          # 菁英比例（前 20%）
CROSSOVER_RATE = 0.8       # 交叉機率
MUTATION_RATE = 0.1        # 突變機率
MUTATION_STRENGTH = 0.2    # 突變強度（基因值的 ±20%）

# ==================== 死亡條件 ====================
# 軀幹接觸地面即為摔倒
TORSO_TOUCH_GROUND_DEATH = True

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
