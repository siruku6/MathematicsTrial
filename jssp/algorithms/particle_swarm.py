import random

import numpy as np
from algorithms.genetic_algorithm import Chromosome, initial_population
from algorithms.simulated_annealing import swap_2_genes
from la40.score_calculator import ScoreCalculator


class Particle:
    """
    粒子群最適化アルゴリズムにおける粒子クラス
    """

    def __init__(self, particle_size: int, num_job: int):
        """
        Parameters
        ------
        particle_size: int
            1つの粒子のサイズ
        num_job: int
            ジョブの数
        """
        self.chromosome: Chromosome = initial_population(
            particle_size, num_job, population_size=1
        )[0]
        self.pbest_chromosome: Chromosome = self.chromosome.copy()  # 個体の最適解
        self.pbest_score = -float("inf")


class PSO_FOR_JSSP:
    """
    Job Shop Scheduling 問題用の粒子群最適化を行うクラス
    """

    def __init__(
        self,
        particle_size: int,
        num_job: int,
        num_particles: int,
        calculator: ScoreCalculator,
        num_local_search: int = 10,
        seed: int = 0,
    ) -> None:
        """
        Parameters
        ------
        particle_size: int
            1つの粒子のサイズ
        num_job: int
            ジョブの数
        num_particles: int
            粒子の数
        calculator: ScoreCalculator
            スコア計算器
        num_local_search: int
            局所探索の回数
        seed: int
            乱数シード
        """
        self.num_particles: int = num_particles
        self.particles: list[Particle] = [
            Particle(particle_size, num_job) for _ in range(num_particles)
        ]

        self.gbest_chromosome: Chromosome = self.particles[
            0
        ].chromosome.copy()  # スワームの最適解
        self.gbest_score = -float("inf")  # 初期化
        self.num_local_search: int = num_local_search
        self._calculator = calculator

        random.seed(seed)
        np.random.seed(seed)

    def calc_score(self, chromosome: Chromosome) -> int:
        return self._calculator.calc_score(chromosome)

    def local_search(self, particle: Particle) -> Particle:
        """
        局所探索を行う

        具体的な処理としては、一つの粒子中の、2か所の遺伝子を入れ替え、
        スコアが改善していれば受け入れ、悪化していれば却下する
        """
        for _ in range(self.num_local_search):
            candidate_chromosome: Chromosome = particle.chromosome.copy()
            candidate_chromosome = swap_2_genes(candidate_chromosome)
            if self.calc_score(candidate_chromosome) > particle.pbest_score:
                particle.chromosome = candidate_chromosome.copy()

        return particle

    def update(self, iteration: int) -> None:
        """
        粒子群の更新を行う
        各粒子の最適解を更新し、スワーム全体の最適解を更新する

        Parameters
        ------
        iteration: int
            現在のイテレーション数
        """
        for particle in self.particles:
            current_score: int = self.calc_score(particle.chromosome)
            if current_score > particle.pbest_score:
                particle.pbest_score = current_score
                particle.pbest_chromosome = particle.chromosome.copy()

            if current_score > self.gbest_score:
                self.gbest_score = current_score
                self.gbest_chromosome = particle.chromosome.copy()
                print(f"Global best [{iteration}]:", self.gbest_score)

        for particle in self.particles:
            particle = self.local_search(particle)

    def show_result(self) -> None:
        """
        最適解を表示する
        """
        print("Best Chromosome:", self.gbest_chromosome)
        print("Best Score:", self.gbest_score)
