import random
from time import time

import numpy as np
from la40.score_calculator import ScoreCalculator
from tqdm import tqdm
from utils.types import Chromosome


def is_replaceable(new_score: float, curr_score: float, T: float) -> bool:
    """
    現在のスコアと新しいスコアを比較し、新しいスコアで置き換えるかどうかを決定する
    """

    def annealing_val(new_score: float, curr_score: float, T: float) -> float:
        return np.exp((new_score - curr_score) / T)

    comparison_val: float = random.random()
    result: bool = (new_score > curr_score) or (
        comparison_val < annealing_val(new_score, curr_score, T)
    )
    return result


def swap_2_genes(chromosome: list[int]) -> list[int]:
    """
    解の中の2つの要素の位置を入れ替える
    """
    num_genes: int = len(chromosome)
    first_idx, second_idx = np.random.randint(num_genes, size=2)
    # print(first_idx, second_idx)

    buf: int = chromosome[first_idx]
    chromosome[first_idx] = chromosome[second_idx]
    chromosome[second_idx] = buf

    return chromosome


def cool(T: float, cooling_rate: float = 0.9) -> float:
    """
    cooling_rate に従って、 simulated annealing における温度を下げる
    """
    return cooling_rate * T


def simulated_annealing(
    calculator: ScoreCalculator,
    curr_solution: list[int],
    T: float = 1.0,
    cooling_rate: float = 0.9,
    steps: int = 100000,
    time_limit: int = 600,  # seconds
) -> tuple[list[dict[str, float]], Chromosome, float, int]:
    """
    与えられた階に対して、simulated annealing を実行する
    """
    curr_score: float = calculator.calc_score(curr_solution)
    best_solution: list[int] = curr_solution.copy()
    best_score: float = curr_score

    hist_scores: list[dict[str, float]] = []
    hist_solutions: list[list[int]] = []
    start_time = time()

    iterated_num: int = 0
    for step in tqdm(range(0, steps), desc="Simulated Annealing"):
        new_chromosome: list[int] = swap_2_genes(curr_solution.copy())
        new_score: int = calculator.calc_score(new_chromosome)

        replaceable: bool = is_replaceable(new_score, curr_score, T)
        if replaceable:
            curr_solution = new_chromosome
            curr_score = new_score

        if new_score > best_score:
            best_solution = new_chromosome
            best_score = new_score

            hist_solutions.append(best_solution)
            hist_scores.append({"step": step, "best_score": best_score})

        if (time() - start_time > time_limit) or (best_score == -1222):
            break

        T = cool(T, cooling_rate=cooling_rate)

    computation_time: float = time() - start_time
    iterated_num = step
    return hist_scores, best_solution, computation_time, iterated_num
