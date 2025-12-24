# ==================== 視窗設定 ====================
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
FPS = 60

# Grid 佈局 
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

# ==================== 生物類型設定 ====================
CREATURE_TYPE = 'QUADRUPED'  # 'BIPED' (雙足) 或 'QUADRUPED' (四足)

# ==================== 生物結構設定 ====================
if CREATURE_TYPE == 'QUADRUPED':
    TORSO_WIDTH = 100              # 軀幹
    TORSO_HEIGHT = 20              
    TORSO_MASS = 8                 # 質量
    MOTOR_COUNT = 8                # 馬達 
    QUADRUPED_LEG_X_OFFSET = 8

    # 四足關節設定
    HIP_MIN_ANGLE = -1.2
    HIP_MAX_ANGLE = 1.2
    KNEE_MIN_ANGLE = -0.5
    KNEE_MAX_ANGLE = 1.5

else:  # BIPED
    TORSO_WIDTH = 60
    TORSO_HEIGHT = 30
    TORSO_MASS = 6
    MOTOR_COUNT = 4                # 4 個馬達 (2 條腿 x 2 關節)
    QUADRUPED_LEG_X_OFFSET = 0

    # 雙足關節設定
    HIP_MIN_ANGLE = -0.8
    HIP_MAX_ANGLE = 0.6
    KNEE_MIN_ANGLE = 0.0
    KNEE_MAX_ANGLE = 1.2

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

# ==================== 關節設定 (共用) ====================
MOTOR_MAX_FORCE = 400000

# ==================== 基因設定 ====================
GENES_PER_MOTOR = 3
GENE_COUNT = GENES_PER_MOTOR * MOTOR_COUNT

AMPLITUDE_MIN = 0.3
AMPLITUDE_MAX = 1.0
FREQUENCY_MIN = 0.5
FREQUENCY_MAX = 2.5
PHASE_MIN = 0.0
PHASE_MAX = 6.28318  # 2π

# ==================== 演化設定 ====================
POPULATION_SIZE = 15           
SIMULATION_TIME = 15.0         
ELITE_RATIO = 0.1
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.2           
MUTATION_STRENGTH = 0.2       

# 選擇策略
SELECTION_METHOD = 'tournament'  # 'roulette' 或 'tournament'
TOURNAMENT_SIZE = 3              # 競賽大小

# 自適應突變設定（用以維持多樣性）
ADAPTIVE_MUTATION = True                
MUTATION_RATE_MAX = 0.5                 
MUTATION_STRENGTH_MAX = 0.4             
DIVERSITY_THRESHOLD = 0.1               # 多樣性閾值

# ==================== 直立判定設定 ====================
# 軀幹高度必須高於此值才算直立
UPRIGHT_HEIGHT_THRESHOLD = 50
# 軀幹角度必須小於此值才算直立
UPRIGHT_ANGLE_THRESHOLD = 0.35

# ==================== 適應度設定 ====================
# 以距離為核心
FITNESS_DISTANCE_WEIGHT = 5.0      # 距離權重
FITNESS_UPRIGHT_WEIGHT = 0.1       # 直立時間權重
FITNESS_SURVIVAL_WEIGHT = 0.0      # 存活時間權重
# 獎勵出現交替踏步（更像走路）
FITNESS_STEP_REWARD = 50.0         # 每次踏步事件的獎勵
STEP_MIN_LEG_DELTA = 15.0          # 腳前後差距門檻

# ==================== 控制器設定 ====================
SHARED_FREQUENCY = True            

# 懲罰設定
FITNESS_FALL_PENALTY = 200.0       # 摔倒懲罰
FITNESS_ENERGY_PENALTY = 0.01      # 能量懲罰

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

# ==================== 反射機制設定 ====================
# 當軀幹傾斜時，調整髖關節輸出
REFLEX_ENABLED = True
REFLEX_BALANCE_GAIN = 1.0          
REFLEX_BALANCE_THRESHOLD = 0.15   # 觸發平衡反射的角度閾值
REFLEX_VELOCITY_GAIN = 0.5        


def set_creature_type(creature_type: str) -> None:
    """更新生物類型，並同步更新所有依賴該類型的結構參數。"""
    global CREATURE_TYPE
    global TORSO_WIDTH, TORSO_HEIGHT, TORSO_MASS
    global MOTOR_COUNT, QUADRUPED_LEG_X_OFFSET
    global HIP_MIN_ANGLE, HIP_MAX_ANGLE, KNEE_MIN_ANGLE, KNEE_MAX_ANGLE
    global GENE_COUNT, EXPECTED_STANDING_HEIGHT

    normalized = (creature_type or "").strip().upper()
    if normalized not in {"BIPED", "QUADRUPED"}:
        raise ValueError(f"Unknown creature type: {creature_type!r}")

    CREATURE_TYPE = normalized

    if CREATURE_TYPE == "QUADRUPED":
        TORSO_WIDTH = 100
        TORSO_HEIGHT = 20
        TORSO_MASS = 8
        MOTOR_COUNT = 8
        QUADRUPED_LEG_X_OFFSET = 8

        HIP_MIN_ANGLE = -1.2
        HIP_MAX_ANGLE = 1.2
        KNEE_MIN_ANGLE = -0.5
        KNEE_MAX_ANGLE = 1.5
    else:  # BIPED
        TORSO_WIDTH = 60
        TORSO_HEIGHT = 30
        TORSO_MASS = 6
        MOTOR_COUNT = 4
        QUADRUPED_LEG_X_OFFSET = 0

        HIP_MIN_ANGLE = -0.8
        HIP_MAX_ANGLE = 0.6
        KNEE_MIN_ANGLE = 0.0
        KNEE_MAX_ANGLE = 1.2

    GENE_COUNT = GENES_PER_MOTOR * MOTOR_COUNT
    EXPECTED_STANDING_HEIGHT = THIGH_LENGTH + SHIN_LENGTH + FOOT_HEIGHT + TORSO_HEIGHT / 2