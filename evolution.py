import random
from config import *


class GeneticAlgorithm:
    def __init__(self):
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.diversity_history = []

        # 自適應突變參數
        self.current_mutation_rate = MUTATION_RATE
        self.current_mutation_strength = MUTATION_STRENGTH

    def create_initial_population(self) -> list:
        # 創建初始族群
        population = []
        for _ in range(POPULATION_SIZE):
            genes = self._random_genes()
            population.append(genes)
        return population

    def _random_genes(self) -> list:
        # 生成隨機基因
        genes = []
        for _ in range(MOTOR_COUNT):
            # 振幅
            genes.append(random.uniform(AMPLITUDE_MIN, AMPLITUDE_MAX))
            # 頻率
            genes.append(random.uniform(FREQUENCY_MIN, FREQUENCY_MAX))
            # 相位
            genes.append(random.uniform(PHASE_MIN, PHASE_MAX))
        return genes

    def evolve(self, population: list, fitness_scores: list) -> list:
        # 執行一次演化
        self.generation += 1

        # 記錄統計資料
        best_fitness = max(fitness_scores)
        avg_fitness = sum(fitness_scores) / len(fitness_scores)
        self.best_fitness_history.append(best_fitness)
        self.avg_fitness_history.append(avg_fitness)

        # 計算並記錄多樣性且更新自適應突變參數
        diversity = self._calculate_diversity(population)
        self.diversity_history.append(diversity)
        self._update_adaptive_mutation(diversity)

        # 將族群按適應度排序
        sorted_pairs = sorted(zip(fitness_scores, population), key=lambda x: x[0], reverse=True)
        sorted_population = [genes for _, genes in sorted_pairs]
        sorted_fitness = [fit for fit, _ in sorted_pairs]

        new_population = []

        # 菁英保留
        elite_count = max(1, int(POPULATION_SIZE * ELITE_RATIO))
        for i in range(elite_count):
            new_population.append(sorted_population[i].copy())

        # 產生剩餘的個體
        while len(new_population) < POPULATION_SIZE:
            # 選擇父母
            parent1 = self._select_parent(sorted_population, sorted_fitness)
            parent2 = self._select_parent(sorted_population, sorted_fitness)

            # 交叉
            if random.random() < CROSSOVER_RATE:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # 突變
            child1 = self._mutate(child1)
            child2 = self._mutate(child2)

            new_population.append(child1)
            if len(new_population) < POPULATION_SIZE:
                new_population.append(child2)

        return new_population

    def _tournament_selection(self, population: list, fitness_scores: list) -> list:
        # 錦標賽選擇
        # 隨機選取參賽者
        indices = random.sample(range(len(population)), min(TOURNAMENT_SIZE, len(population)))

        # 找出適應度最高的
        winner_idx = max(indices, key=lambda i: fitness_scores[i])

        return population[winner_idx].copy()

    def _select_parent(self, population: list, fitness_scores: list) -> list:
        # 根據設定選擇父母
        if SELECTION_METHOD == 'tournament':
            return self._tournament_selection(population, fitness_scores)
        else:
            return self._roulette_selection(population, fitness_scores)

    def _roulette_selection(self, population: list, fitness_scores: list) -> list:
        # 輪盤選擇
        # 將適應度轉換為正數
        min_fitness = min(fitness_scores)
        adjusted_fitness = [f - min_fitness + 1 for f in fitness_scores]

        total_fitness = sum(adjusted_fitness)
        if total_fitness == 0:
            return random.choice(population).copy()

        # 輪盤選擇
        pick = random.uniform(0, total_fitness)
        current = 0
        for i, fitness in enumerate(adjusted_fitness):
            current += fitness
            if current >= pick:
                return population[i].copy()

        return population[-1].copy()

    def _calculate_diversity(self, population: list) -> float:
        # 計算族群多樣性
        if len(population) < 2:
            return 1.0

        gene_count = len(population[0])
        total_variance = 0.0

        for gene_idx in range(gene_count):
            # 收集所有個體在這個基因位置的值
            gene_values = [individual[gene_idx] for individual in population]

            # 計算標準差
            mean = sum(gene_values) / len(gene_values)
            variance = sum((v - mean) ** 2 for v in gene_values) / len(gene_values)
            std_dev = variance ** 0.5

            # 根據基因類型正規化
            gene_type = gene_idx % GENES_PER_MOTOR
            if gene_type == 0:  # 振幅
                gene_range = AMPLITUDE_MAX - AMPLITUDE_MIN
            elif gene_type == 1:  # 頻率
                gene_range = FREQUENCY_MAX - FREQUENCY_MIN
            else:  # 相位
                gene_range = PHASE_MAX - PHASE_MIN

            normalized_std = std_dev / gene_range if gene_range > 0 else 0
            total_variance += normalized_std

        # 平均多樣性
        diversity = total_variance / gene_count

        return min(1.0, diversity)

    def _update_adaptive_mutation(self, diversity: float):
        # 根據多樣性調整突變參數
        if not ADAPTIVE_MUTATION:
            return

        if diversity < DIVERSITY_THRESHOLD:
            # 多樣性低，提高突變
            ratio = 1.0 - (diversity / DIVERSITY_THRESHOLD)

            self.current_mutation_rate = MUTATION_RATE + ratio * (MUTATION_RATE_MAX - MUTATION_RATE)
            self.current_mutation_strength = MUTATION_STRENGTH + ratio * (MUTATION_STRENGTH_MAX - MUTATION_STRENGTH)
        else:
            # 多樣性足夠，使用基礎突變率
            self.current_mutation_rate = MUTATION_RATE
            self.current_mutation_strength = MUTATION_STRENGTH

    def _crossover(self, parent1: list, parent2: list) -> tuple:
        # 單點交叉 (混合)
        crossover_point = random.randint(1, MOTOR_COUNT - 1) * GENES_PER_MOTOR

        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]

        return child1, child2

    def _mutate(self, genes: list) -> list:
        # 高斯突變
        mutated = genes.copy()

        # 使用自適應的突變參數
        mutation_rate = self.current_mutation_rate
        mutation_strength = self.current_mutation_strength

        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                gene_type = i % GENES_PER_MOTOR

                if gene_type == 0:  # 振幅
                    mutation = random.gauss(0, mutation_strength * (AMPLITUDE_MAX - AMPLITUDE_MIN))
                    mutated[i] = max(AMPLITUDE_MIN, min(AMPLITUDE_MAX, mutated[i] + mutation))
                elif gene_type == 1:  # 頻率
                    mutation = random.gauss(0, mutation_strength * (FREQUENCY_MAX - FREQUENCY_MIN))
                    mutated[i] = max(FREQUENCY_MIN, min(FREQUENCY_MAX, mutated[i] + mutation))
                else:  # 相位
                    mutation = random.gauss(0, mutation_strength * (PHASE_MAX - PHASE_MIN))
                    mutated[i] = (mutated[i] + mutation) % PHASE_MAX  # wrap around

        return mutated

    def get_statistics(self) -> dict:
        # 獲取演化統計資料

        return {
            'generation': self.generation,
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'diversity_history': self.diversity_history,
            'current_best': self.best_fitness_history[-1] if self.best_fitness_history else 0,
            'current_avg': self.avg_fitness_history[-1] if self.avg_fitness_history else 0,
            'current_diversity': self.diversity_history[-1] if self.diversity_history else 1.0,
            'current_mutation_rate': self.current_mutation_rate,
            'current_mutation_strength': self.current_mutation_strength,
        }