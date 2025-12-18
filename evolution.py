"""
步履蹣跚：基於物理引擎的 2D 生物行走演化
遺傳演算法模組
"""

import random
from config import *


class GeneticAlgorithm:
    """
    遺傳演算法

    選擇策略：菁英保留 + 輪盤選擇
    交叉方式：單點交叉
    突變方式：高斯突變
    """

    def __init__(self):
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []

    def create_initial_population(self) -> list:
        """
        創建初始族群

        Returns:
            基因列表的列表
        """
        population = []
        for _ in range(POPULATION_SIZE):
            genes = self._random_genes()
            population.append(genes)
        return population

    def _random_genes(self) -> list:
        """生成隨機基因"""
        genes = []
        for _ in range(MOTOR_COUNT):
            # 振幅 A
            genes.append(random.uniform(AMPLITUDE_MIN, AMPLITUDE_MAX))
            # 頻率 ω
            genes.append(random.uniform(FREQUENCY_MIN, FREQUENCY_MAX))
            # 相位 φ
            genes.append(random.uniform(PHASE_MIN, PHASE_MAX))
        return genes

    def evolve(self, population: list, fitness_scores: list) -> list:
        """
        執行一次演化

        Args:
            population: 當前族群的基因列表
            fitness_scores: 對應的適應度分數

        Returns:
            新一代族群的基因列表
        """
        self.generation += 1

        # 記錄統計資料
        best_fitness = max(fitness_scores)
        avg_fitness = sum(fitness_scores) / len(fitness_scores)
        self.best_fitness_history.append(best_fitness)
        self.avg_fitness_history.append(avg_fitness)

        # 將族群按適應度排序
        sorted_pairs = sorted(zip(fitness_scores, population), key=lambda x: x[0], reverse=True)
        sorted_population = [genes for _, genes in sorted_pairs]
        sorted_fitness = [fit for fit, _ in sorted_pairs]

        new_population = []

        # 1. 菁英保留：保留前 ELITE_RATIO 的個體
        elite_count = max(1, int(POPULATION_SIZE * ELITE_RATIO))
        for i in range(elite_count):
            new_population.append(sorted_population[i].copy())

        # 2. 產生剩餘的個體（透過選擇、交叉、突變）
        while len(new_population) < POPULATION_SIZE:
            # 選擇兩個親代
            parent1 = self._roulette_selection(sorted_population, sorted_fitness)
            parent2 = self._roulette_selection(sorted_population, sorted_fitness)

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

    def _roulette_selection(self, population: list, fitness_scores: list) -> list:
        """
        輪盤選擇

        Args:
            population: 族群
            fitness_scores: 適應度分數（已排序）

        Returns:
            選中的個體基因
        """
        # 將適應度轉換為正數（加上偏移量）
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

    def _crossover(self, parent1: list, parent2: list) -> tuple:
        """
        單點交叉

        Args:
            parent1: 親代 1
            parent2: 親代 2

        Returns:
            (child1, child2) 子代元組
        """
        # 選擇交叉點（以馬達為單位，每個馬達 3 個基因）
        crossover_point = random.randint(1, MOTOR_COUNT - 1) * GENES_PER_MOTOR

        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]

        return child1, child2

    def _mutate(self, genes: list) -> list:
        """
        高斯突變（改進版：相位使用 wrap 而非 clamp）

        Args:
            genes: 基因列表

        Returns:
            突變後的基因列表
        """
        mutated = genes.copy()

        for i in range(len(mutated)):
            if random.random() < MUTATION_RATE:
                gene_type = i % GENES_PER_MOTOR

                if gene_type == 0:  # 振幅
                    mutation = random.gauss(0, MUTATION_STRENGTH * (AMPLITUDE_MAX - AMPLITUDE_MIN))
                    mutated[i] = max(AMPLITUDE_MIN, min(AMPLITUDE_MAX, mutated[i] + mutation))
                elif gene_type == 1:  # 頻率
                    mutation = random.gauss(0, MUTATION_STRENGTH * (FREQUENCY_MAX - FREQUENCY_MIN))
                    mutated[i] = max(FREQUENCY_MIN, min(FREQUENCY_MAX, mutated[i] + mutation))
                else:  # 相位（使用 wrap 而非 clamp，避免邊界堆積）
                    mutation = random.gauss(0, MUTATION_STRENGTH * (PHASE_MAX - PHASE_MIN))
                    mutated[i] = (mutated[i] + mutation) % PHASE_MAX  # wrap around

        return mutated

    def get_statistics(self) -> dict:
        """
        獲取演化統計資料

        Returns:
            統計資料字典
        """
        return {
            'generation': self.generation,
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'current_best': self.best_fitness_history[-1] if self.best_fitness_history else 0,
            'current_avg': self.avg_fitness_history[-1] if self.avg_fitness_history else 0,
        }
