import numpy as np
from tqdm import tqdm

# 100 個の int 型要素を持つ配列
Chromosome = list[int]


class GA:
    def __init__(
        self,
        population_size: int,
        num_job: int,
        num_machine: int,
        num_gene: int,
        proc_time: list,
        machine_type_seq: list,
        machine_num_per_type: list[int],
    ) -> None:
        self.population_size = population_size
        self.num_job = num_job
        self.num_machine = num_machine
        self.num_gene = num_gene
        self.proc_time = proc_time
        self.machine_type_seq = machine_type_seq
        self.machine_num_per_type = machine_num_per_type

        self.results: list[dict] = []

    def inital_population(self, population_size: int) -> list[Chromosome]:
        """
        初期の1世代分の個体を生成する
        """
        population_list: list = []
        for i in range(population_size):
            # generate a random permutation of 0 to num_job * num_mc - 1
            ini_pop: list = list(np.random.permutation(self.num_gene) % self.num_job)

            # convert to job number format, every job appears m(num_job) times
            population_list.append(ini_pop)
        return population_list

    def crossover(
        self, population_list: list[Chromosome], crossover_rate: float
    ) -> tuple[list[Chromosome], list[Chromosome]]:
        """
        2点交叉を行う
        """
        parent_list: list[Chromosome] = (
            population_list.copy()
        )  # preserve the original parent chromosomes
        offspring_list: list[Chromosome] = population_list.copy()

        # 產生一個組合去選擇用哪幾組父代染色體進行交配
        # 組み合わせを生成して、交配に使用する親染色体のセットを選択します
        parent_sequence = list(np.random.permutation(self.population_size))
        for i in range(0, self.population_size, 2):
            crossover_prob = np.random.rand()
            if crossover_prob <= crossover_rate:
                parent_1 = population_list[parent_sequence[i]][:]
                parent_2 = population_list[parent_sequence[i + 1]][:]
                child_1 = parent_1[:]
                child_2 = parent_2[:]
                # 產生2個不同的交配點，並由小到大排序
                # 2つの異なる交点を生成し、小さいものから大きいものに並べ替えます。
                crossover_point = list(
                    np.random.choice(self.num_gene, 2, replace=False)
                )
                crossover_point.sort()

                # parent_2中間的基因移到parent_1中間，產生child1
                # parent_2 の中央にある遺伝子がparent_1 の中央に移動され、child1 が生成されます。
                child_1[crossover_point[0] : crossover_point[1]] = parent_2[
                    crossover_point[0] : crossover_point[1]
                ]
                # parent_1中間的基因移到parent_2中間，產生child2
                child_2[crossover_point[0] : crossover_point[1]] = parent_1[
                    crossover_point[0] : crossover_point[1]
                ]

                offspring_list[parent_sequence[i]] = child_1[:]
                offspring_list[parent_sequence[i + 1]] = child_2[:]
        return parent_list, offspring_list

    # 染色体内の各アーティファクトの発生数は 10 ですが、上記の交配作用により、一部の染色体におけるアーティファクトの発生数は 10 未満または 10 を超え、
    # 実行不可能なスケジューリング ソリューションが形成されるため、ここで次のことを行う必要があります。
    # 実行不可能な染色体が修復作用を受けて実行可能なスケジュールになることに焦点を当てる
    def repairmet(self, offspring_list: list[Chromosome]) -> list[Chromosome]:
        stop = True

        # 不斷進行修復，直到每個job的出現次數等於machine數
        # 各ジョブの発生回数がマシンの台数と同じになるまで修復を続ける。
        while stop:
            for i in range(self.population_size):
                # 計算每個job的出現次數 (各ジョブの発生回数を計算する)
                unique_elements, counts = np.unique(
                    offspring_list[i], return_counts=True
                )
                # 有多餘job和缺少的job (余分なジョブ または 不足しているジョブがある場合)
                if sum(counts != self.num_machine) != 0:
                    job_ids = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
                    missing_ids = set(unique_elements) - job_ids
                    if len(missing_ids) == 0:
                        # 出現次數缺少的job (出現回数が少ないジョブ)
                        less_job = unique_elements[np.argmin(counts)]
                        # 出現次數多出的job (出現回数が余分なジョブ)
                        large_job = unique_elements[np.argmax(counts)]
                    # NOTE: おそらくこの分岐が存在しなかったため、後続処理でエラーが発生していたと思料される
                    else:
                        less_job = list(missing_ids)[0]
                        large_job = unique_elements[np.argmax(counts)]

                    offspring_array = np.array(offspring_list[i])

                    try:
                        # NOTE: ごくたまに、 IndexError: index 0 is out of bounds for axis 0 with size 0 が発生する
                        # 出現次數多出的job的第一個出現位置 (最初に出現する余分なジョブの位置)
                        offspring_job_large_index = np.where(
                            offspring_array == large_job
                        )[0][0]
                    # TODO: error の原因究明のためデバッグ中
                    except IndexError as error:
                        print(error)
                        print("large_job:", large_job, "less_job:", less_job)
                        print(
                            "np.where(offspring_array == large_job):",
                            np.where(offspring_array == large_job),
                        )
                        # import pdb; pdb.set_trace()

                    # 出現次數的多的job， 使用較少出現的job替代
                    offspring_list[i][offspring_job_large_index] = less_job

            counts_sum = 0
            for j in range(
                self.population_size
            ):  # 檢查每隔chromosome是否出現異常的情況
                unique_elements, counts = np.unique(
                    offspring_list[j], return_counts=True
                )
                if sum(counts != self.num_machine) != 0:
                    counts_sum += 1
            if counts_sum == 0:
                stop = False
        return offspring_list

    def mutation(
        self,
        offspring_list: list[Chromosome],
        mutation_rate: float,
        num_mutation_jobs: int,
    ) -> list[Chromosome]:
        for i in range(self.population_size):
            mutation_prob = np.random.rand()
            if mutation_prob <= mutation_rate:
                mutation_position = list(
                    np.random.choice(self.num_gene, num_mutation_jobs, replace=False)
                )  # 選擇突變的位置
                muta_list = []
                for j in mutation_position:
                    muta_list.append(offspring_list[i][j])  # 要突變的基因list
                muta_list.append(muta_list[0])  # 尾部加上第一個基因
                muta_list.pop(0)  # 將第一個基因刪除
                count = 0
                for k in mutation_position:
                    offspring_list[i][k] = muta_list[
                        count
                    ]  # 將用突變後的基因取代原本的
                    count += 1
        return offspring_list

    def _calc_time4job(
        self, target_chromosome: Chromosome, num_job: int, num_machine: int
    ) -> dict[int, int]:
        """
        対象個体の遺伝子をスケジュールにしたときに、実際にどのくらい時間がかかるかを計算する

        len(target_chromosome) => num_job * num_machine
        """
        j_keys: list[int] = [j for j in range(num_job)]
        m_keys: list[int] = [j for j in range(0, num_machine)]

        # job の key 番目のタスクが処理された回数をカウントする
        key_count: dict[int, int] = {key: 0 for key in j_keys}

        # 各 job にかかる時間を格納するための辞書
        time4job: dict[int, int] = {key: 0 for key in j_keys}

        time4machine: dict[int, dict[int, int]] = {}
        for machine_type_id in m_keys:
            time4machine[machine_type_id + 1] = {}
            for machine_id in range(0, self.machine_num_per_type[machine_type_id]):
                time4machine[machine_type_id + 1][machine_id] = 0

        # 1個体の染色体を一つずつ処理
        for gene in target_chromosome:
            # 次に処理すべきタスクのID
            task_no: int = key_count[gene]

            # 処理時間
            gen_t: int = int(self.proc_time[gene][task_no])
            # ジョブ内タスクを担当する機械タイプのID
            m_type_id: int = int(self.machine_type_seq[gene][task_no])

            # OPTIMIZE: ここでは、余計な待機時間が少なくて済む機械を選びたいが、暫定で単純な処理とした
            # タスクを担当する機械IDをここで決める (今まで処理時間が最も短い機械)
            machine_id: int = min(
                time4machine[m_type_id], key=time4machine[m_type_id].get
            )
            # machine_id: int = min(time4machine[m_type_id])

            # gene番目のジョブ内のタスク実行にかかった時間合計
            time4job[gene] = time4job[gene] + gen_t

            # m_type_id 番目の機械における処理時間合計
            time4machine[m_type_id][machine_id] = (
                time4machine[m_type_id][machine_id] + gen_t
            )

            # ジョブ毎にかかった時間、もしくは機械毎にかかった時間のうち、小さい方を、大きい方の値で上書きする
            if time4machine[m_type_id][machine_id] < time4job[gene]:
                time4machine[m_type_id][machine_id] = time4job[gene]
            elif time4machine[m_type_id][machine_id] > time4job[gene]:
                time4job[gene] = time4machine[m_type_id][machine_id]

            key_count[gene] = key_count[gene] + 1

        return time4job

    def fitness_caculate(self, total_chromosome: list[Chromosome]) -> tuple:
        """
        適応度の計算を行う

        Partameters
        ------
        total_chromosome: list[Chromosome]
            parent and offspring

        Returns
        ------
        chrom_fit: list[int]
            各染色体から計算された makespan の配列 (小さい方が良い)

        chrom_fitness: list[float]
            各染色体から計算された makespan の逆数の配列 (大きい方が良い)

        total_fitness: int
            各染色体から計算された makespan の逆数の合計 (大きい方が良い)
        """
        chrom_fitness, chrom_fit = [], []
        total_fitness: int = 0
        for individual_id in range(
            self.population_size * 2
        ):  # 親と子の2世代分ループするので 2倍
            time4job: dict[int, int] = self._calc_time4job(
                total_chromosome[individual_id], self.num_job, self.num_machine
            )

            # 在job中需要的最多完工時間的，即為makespan
            # 最も時間がかかる仕事は makespan である。
            makespan = max(time4job.values())
            # 因後續採用輪盤法時要最小化完工時間，因此每個chromosome所算出的適應值必須以倒數的方式記錄
            # 各染色体について計算された適応値は、その後ルーレットホイール法を使用する際の完了時間を最小にするために、逆順に記録されなければならない。
            chrom_fitness.append(1 / makespan)

            # 計算每個chromosome原本的總完工時間
            # 各染色体の元完了時間の合計を計算する。
            chrom_fit.append(makespan)
            total_fitness = total_fitness + chrom_fitness[individual_id]

        return chrom_fit, chrom_fitness, total_fitness

    def selection(
        self,
        chrom_fitness: list[int],
        total_fitness: float,
        total_chromosome: list[Chromosome],
        population_list: list[Chromosome],
    ) -> list[Chromosome]:
        """
        selection(roulette wheel approach)
        """
        fitness_prob, fitness_cumulate_prob = [], []

        for i in range(self.population_size * 2):
            # 計算每個chromosome的fitness，佔所有chromosome的比例
            # 各染色体のフィットネスを全染色体に占める割合で計算する。
            fitness_prob.append(chrom_fitness[i] / total_fitness)
        for i in range(self.population_size * 2):
            cumulative: float = 0
            # 計算每個chromosome的fitness累績機率。
            # 各染色体のフィットネス発生率を計算する。
            for j in range(0, i + 1):
                cumulative = cumulative + fitness_prob[j]
            fitness_cumulate_prob.append(cumulative)

        # 產生一組size為population大小的隨機數list
        # 母集団の大きさを持つ乱数のリストを生成する。
        selection_rand = [np.random.rand() for i in range(self.population_size)]

        # 選出新的一組Population
        # 新しい population を選択する
        for i in range(self.population_size):
            # 若第一組被選中時，將第一組chromosome加入
            # 最初の組合せが選択されたら、最初の染色体を加える
            if selection_rand[i] <= fitness_cumulate_prob[0]:
                population_list[i] = total_chromosome[0].copy()
            else:
                for j in range(0, self.population_size * 2 - 1):
                    if (
                        selection_rand[i] > fitness_cumulate_prob[j]
                        and selection_rand[i] <= fitness_cumulate_prob[j + 1]
                    ):
                        population_list[i] = total_chromosome[j + 1].copy()
                        break
        return population_list

    def comparsion(
        self, chrom_fit: list[float], total_chromosome: list[Chromosome]
    ) -> tuple[float, Chromosome]:
        Tbest_current = 99999999999  # population中最好的染色體
        for i in range(self.population_size * 2):
            if chrom_fit[i] < Tbest_current:  # 找出population中最小的itness
                Tbest_current: float = chrom_fit[i]
                sequence_current: Chromosome = total_chromosome[
                    i
                ].copy()  # 儲存population中有最小fitness的染色體
        return Tbest_current, sequence_current

    def run(
        self,
        num_iteration: int,
        crossover_rate: float,
        mutation_rate: float,
        mutation_selection_rate: float,
    ) -> None:
        num_mutation_jobs = round(self.num_gene * mutation_selection_rate)

        Tbest = 999999999999999
        makespan_record = []
        best_chromosome_history: list = []
        # generate initial population
        population_list = self.inital_population(population_size=self.population_size)

        for iter in tqdm(range(num_iteration)):
            # generate offspring by crossover
            parent_list, offspring_list = self.crossover(
                population_list=population_list, crossover_rate=crossover_rate
            )

            # offspring repairment
            offspring_list = self.repairmet(offspring_list)

            # offspring mutation
            offspring_list = self.mutation(
                offspring_list,
                mutation_rate=mutation_rate,
                num_mutation_jobs=num_mutation_jobs,
            )

            # all chromosome：parent and offspring
            total_chromosome = parent_list.copy() + offspring_list.copy()

            # calculate fitness for each chromosome
            chrom_fit, chrom_fitness, total_fitness = self.fitness_caculate(
                total_chromosome
            )

            # select the new population
            population_list = self.selection(
                chrom_fitness, total_fitness, total_chromosome, population_list
            )

            # comparision
            Tbest_current, sequence_current = self.comparsion(
                chrom_fit, total_chromosome
            )
            # 將目前這代population中最好的染色體，與迭代過程中最好的比較
            # 現在の世代の集団で最も優れた染色体を、反復プロセスで最も優れた染色体と比較します。
            if Tbest_current <= Tbest:
                Tbest = Tbest_current
                sequence_best: Chromosome = sequence_current.copy()
                best_chromosome_history.append(sequence_best)

            makespan_record.append(Tbest)

        self.results.append(
            {
                "best_make_span": Tbest,
                "makespan_record": makespan_record,
                "sequence_best": sequence_best,
                "best_chromosome_history": best_chromosome_history,
            }
        )
