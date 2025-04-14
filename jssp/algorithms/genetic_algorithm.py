import numpy as np
from utils.types import Chromosome


def initial_population(
    num_gene: int, num_job: int, population_size: int
) -> list[Chromosome]:
    """
    初期の1世代分の個体を生成する

    Parameters
    ------
    num_gene: int
        1個体における遺伝子の数
    num_job: int
        ジョブの数
    population_size: int
        生成する個体の数
    """
    population_list: list[Chromosome] = []
    for i in range(population_size):
        # generate a random permutation of 0 to num_job * num_mc - 1
        ini_pop: Chromosome = list(np.random.permutation(num_gene) % num_job)

        # convert to job number format, every job appears m(num_job) times
        population_list.append(ini_pop)
    return population_list


def crossover_by_order(
    population_list: np.ndarray,
    num_jobs: int,
    crossover_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    順序に基づく交叉を行う

    Parameters
    ------
    population_list: np.ndarray
        個体群 (2-dim: (population_size, num_gene))
    num_jobs: int
        ジョブ数
    crossover_rate: float
        交叉率

    Returns
    ------
    parent_list: np.ndarray
        親の個体群 (2-dim: (population_size, num_gene))
    offspring_list: np.ndarray
        子の個体群 (2-dim: (population_size, num_gene))
    """
    # preserve the original parent chromosomes
    parent_list: np.ndarray = population_list.copy()
    offspring_list: np.ndarray = population_list.copy()

    population_size: int = len(population_list)
    # 個体群をシャッフルして、2個体ずつ親とする
    parent_sequence = np.random.permutation(population_size)
    for i in range(0, population_size, 2):
        # 親を確定
        parent_1: np.ndarray = population_list[parent_sequence[i], :]
        parent_2: np.ndarray = population_list[parent_sequence[i + 1], :]

        # 子の染色体の器を生成
        child_1: np.ndarray = parent_1[:].copy()
        child_2: np.ndarray = parent_2[:].copy()

        # 交叉対象とするジョブのリストを作成する
        # それぞれの親から、もう一方の親へ移される ジョブID のリスト
        target_jobs1: np.ndarray = np.array([])
        target_jobs2: np.ndarray = np.array([])
        for job_id in range(0, num_jobs):
            crossover_prob1: float = np.random.rand()
            crossover_prob2: float = np.random.rand()
            if crossover_prob1 <= crossover_rate:
                target_jobs1 = np.append(target_jobs1, job_id)
            if crossover_prob2 <= crossover_rate:
                target_jobs2 = np.append(target_jobs2, job_id)

        # 置き換えられる遺伝子座を決定
        # (相手の親が移そうとしているジョブIDがセットされている遺伝子座)
        ids_replaced1 = np.where(np.isin(parent_1, target_jobs2))
        ids_replaced2 = np.where(np.isin(parent_2, target_jobs1))

        # もう一方の個体に移される遺伝子座を決定
        # (自個体が移そうしているジョブIDがせっとされている遺伝子座)
        ids_replacing1 = np.where(np.isin(parent_1, target_jobs1))
        ids_replacing2 = np.where(np.isin(parent_2, target_jobs2))

        # それぞれの親の指定遺伝子座の遺伝子を置き換え
        child_1[ids_replaced1] = parent_2[ids_replacing2]
        child_2[ids_replaced2] = parent_1[ids_replacing1]

        # 子の染色体を保存
        offspring_list[parent_sequence[i]] = child_1[:]
        offspring_list[parent_sequence[i + 1]] = child_2[:]

    return parent_list, offspring_list
