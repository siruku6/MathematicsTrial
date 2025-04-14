from utils.types import Chromosome


class ScoreCalculator:
    def __init__(
        self,
        processing_times: list[list[int]],
        machine_sequenses: list[list[int]],
    ) -> None:
        self.processing_times: list[list[int]] = processing_times
        self.machine_sequences: list[list[int]] = machine_sequenses
        self.num_job: int = len(processing_times)
        self.num_machine: int = len(processing_times[0])

    def calc_time4job(self, target_chromosome: Chromosome) -> dict[int, int]:
        """
        対象個体の遺伝子をスケジュールにしたときに、実際にどのくらい時間がかかるかを計算する

        len(target_chromosome) => num_job * num_machine
        """
        j_keys: list[int] = [j for j in range(self.num_job)]
        # job の key 番目のタスクが処理された回数をカウントする
        key_count: dict[int, int] = {key: 0 for key in j_keys}

        # 各 job にかかる時間を格納するための辞書
        time4job: dict[int, int] = {key: 0 for key in j_keys}

        m_keys: list[int] = [j + 1 for j in range(self.num_machine)]
        time4machine: dict[int, int] = {key: 0 for key in m_keys}

        # 1個体の染色体を一つずつ処理
        for i in target_chromosome:
            # 次に処理すべきタスクのID
            task_no: int = key_count[i]

            # 処理時間
            gen_t: int = int(self.processing_times[i][task_no])
            # ジョブにおける、機械の処理順
            gen_m: int = int(self.machine_sequences[i][task_no])

            # i番目のジョブ内のタスク実行にかかった時間合計
            time4job[i] = time4job[i] + gen_t
            # gen_m 番目の機械における処理時間合計
            time4machine[gen_m] = time4machine[gen_m] + gen_t

            # ジョブ毎にかかった時間、もしくは機械毎にかかった時間のうち、小さい方を、大きい方の値で上書きする
            if time4machine[gen_m] < time4job[i]:
                time4machine[gen_m] = time4job[i]
            elif time4machine[gen_m] > time4job[i]:
                time4job[i] = time4machine[gen_m]

            key_count[i] = key_count[i] + 1
        return time4job

    def calc_score(self, target_chromosome: Chromosome) -> int:
        time4job: dict[int, int] = self.calc_time4job(target_chromosome)
        max_makespan: int = max(time4job.values())

        return -max_makespan
