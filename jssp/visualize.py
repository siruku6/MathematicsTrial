# import matplotlib.pyplot as plt
# import plotly.plotly as py
# # from chart_studio import plotly as py
# from plotly.offline import iplot

# import plotly.figure_factory as ff
import datetime

from genetic_algorithm import Chromosome


def prepare_gannt_data_from(
    machine_num_per_type: list[int],  # 0~9
    proc_time: list[list[int]],
    machine_type_seq: list[list[int]],
    m_keys: list[int],  # 0~9
    j_keys: list[int],  # 0~9
    sequence_best: Chromosome,
) -> tuple[dict, dict]:
    key_count = {key: 0 for key in j_keys}
    j_count = {key: 0 for key in j_keys}
    # m_count = {key: 0 for key in m_keys}
    time4machine: dict[int, dict[int, int]] = {}
    for machine_type_id in m_keys:
        time4machine[machine_type_id + 1] = {}
        for machine_id in range(0, machine_num_per_type[machine_type_id]):
            time4machine[machine_type_id + 1][machine_id] = 0

    j_record: dict = {}

    for gene in sequence_best:
        # 次に処理すべきタスクのID
        task_no: int = key_count[gene]

        # 処理時間
        gen_t: int = int(proc_time[gene][task_no])

        # ジョブ内タスクを担当する機械タイプのID
        # gen_m: int = int(machine_type_seq[gene][task_no])
        m_type_id: int = int(machine_type_seq[gene][task_no])
        # タスクを担当する機械IDをここで決める (今まで処理時間が最も短い機械)
        machine_id: int = min(
            time4machine[m_type_id],
            key=time4machine[m_type_id].get,
        )

        j_count[gene] = j_count[gene] + gen_t
        time4machine[m_type_id][machine_id] = (
            time4machine[m_type_id][machine_id] + gen_t
        )

        if time4machine[m_type_id][machine_id] < j_count[gene]:
            time4machine[m_type_id][machine_id] = j_count[gene]
        elif time4machine[m_type_id][machine_id] > j_count[gene]:
            j_count[gene] = time4machine[m_type_id][machine_id]

        # convert seconds to hours, minutes and seconds
        start_time: str = str(
            datetime.timedelta(seconds=j_count[gene] - proc_time[gene][task_no])
        )
        end_time: str = str(datetime.timedelta(seconds=j_count[gene]))

        rec_key: tuple = (gene, f"{m_type_id}_{machine_id}")

        if j_record.get(rec_key) is not None:
            print(rec_key, "is already in j_record, and updated.")
        j_record[rec_key] = [start_time, end_time]

        key_count[gene] = key_count[gene] + 1

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
