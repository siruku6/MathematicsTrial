# import matplotlib.pyplot as plt
# import plotly.plotly as py
# # from chart_studio import plotly as py
# from plotly.offline import iplot

# import plotly.figure_factory as ff

from eval_score import make_job_record
from genetic_algorithm import Chromosome


def prepare_gannt_data_from(
    machine_num_per_type: list[int],  # 0~9
    proc_time: list[list[int]],
    machine_type_seq: list[list[int]],
    m_keys: list[int],  # 0~9
    j_keys: list[int],  # 0~9
    sequence_best: Chromosome,
) -> tuple[dict, dict]:
    # カウンター類の初期化
    done_count_in_job = {key: 0 for key in j_keys}
    time4job = {key: 0 for key in j_keys}
    time4machine: dict[int, dict[int, int]] = {}
    for machine_type_id in m_keys:
        time4machine[machine_type_id + 1] = {}
        for machine_id in range(0, machine_num_per_type[machine_type_id]):
            time4machine[machine_type_id + 1][machine_id] = 0
    # free_times: list[dict[str, int]] = [
    #     # 例
    #     # {
    #     #     "start_time": 4, "end_time": 12, "interval": 8,
    #     #     "machine_type_id": 2, "machine_id": 0
    #     # }
    # ]

    j_record: dict = {}
    for gene in sequence_best:
        # 次に処理すべきタスクのID
        task_no: int = done_count_in_job[gene]

        # 処理時間
        gen_t: int = int(proc_time[gene][task_no])

        # ジョブ内タスクを担当する機械タイプのID
        # gen_m: int = int(machine_type_seq[gene][task_no])
        m_type_id: int = int(machine_type_seq[gene][task_no])
        # タスクを担当する機械IDをここで決める (今まで処理時間が最も短い機械)
        machine_id: int = min(time4machine[m_type_id], key=time4machine[m_type_id].get)

        time4job[gene] = time4job[gene] + gen_t
        time4machine[m_type_id][machine_id] = (
            time4machine[m_type_id][machine_id] + gen_t
        )

        if time4machine[m_type_id][machine_id] < time4job[gene]:
            time4machine[m_type_id][machine_id] = time4job[gene]
        elif time4machine[m_type_id][machine_id] > time4job[gene]:
            time4job[gene] = time4machine[m_type_id][machine_id]

        # 記録を残す
        j_record = j_record | make_job_record(
            time4job, gene, gen_t, m_type_id, machine_id, j_record
        )
        done_count_in_job[gene] = done_count_in_job[gene] + 1

    return time4machine, j_record


def format_gannt_data(
    machine_num_per_type: list[int],  # 0~9
    m_keys: list[int],  # 0~9
    j_keys: list[int],  # 0~9
    j_record: dict[tuple, list[str]],
) -> list[dict]:
    frame_dicts: list[dict] = []
    for m_type_id in m_keys:
        for j in j_keys:
            for machine_id in range(0, machine_num_per_type[m_type_id]):
                if j_record.get((j, f"{m_type_id + 1}_{machine_id}")) is None:
                    continue
                frame_dicts.append(
                    dict(
                        Task=f"Machine {m_type_id}-{machine_id}",
                        Start="2023-10-15 %s"
                        % (str(j_record[(j, f"{m_type_id + 1}_{machine_id}")][0])),
                        Finish="2023-10-15 %s"
                        % (str(j_record[(j, f"{m_type_id + 1}_{machine_id}")][1])),
                        Resource="Job %s" % (j + 1),
                    )
                )
                # df.append(dict(Task="Machine %s"%(m), Start="2018-07-14 %s"%(str(j_record[(j,m)][0])), Finish="2018-07-14 %s"%(str(j_record[(j,m)][1])),Resource="Job %s"%(j+1)))

    # NOTE: Machine 順にソートすることで、Gannt チャートの見た目を毎回統一する
    frame_dicts = sorted(frame_dicts, key=lambda x: x["Task"])
    return frame_dicts
