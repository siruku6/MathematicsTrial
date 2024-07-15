# import matplotlib.pyplot as plt
# import plotly.plotly as py
# # from chart_studio import plotly as py
# from plotly.offline import iplot

# import plotly.figure_factory as ff


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
