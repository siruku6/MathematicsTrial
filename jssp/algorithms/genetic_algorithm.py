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
