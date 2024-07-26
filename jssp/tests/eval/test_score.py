from jssp.eval.score import calc_time4job, prepare_gannt_data_from


class TestCalcTime4Job:
    def test_all_flow_jobs(self) -> None:
        tool_num_per_type = [1, 1, 1]
        proc_time = [[1, 2, 3], [3, 2, 1], [4, 1, 1]]
        tool_type_seq = [[1, 2, 3], [3, 2, 1], [2, 1, 3]]
        num_job = 3
        num_tool_types = 3
        target_chromosome = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        OperationTypeMapping = {0: "flow", 1: "flow", 2: "flow"}

        result = calc_time4job(
            tool_num_per_type,
            proc_time,
            tool_type_seq,
            num_job,
            num_tool_types,
            target_chromosome,
            OperationTypeMapping,
        )

        # 各マシンタイプの各マシンの稼働終了時間の例
        # assert result == {1: {0: 16}, 2: {0: 15}, 3: {0: 17}}

        # 各ジョブの終了時刻
        assert result == {0: 6, 1: 12, 2: 17}


class TestPrepareGanntDataFrom:
    def test_all_flow_jobs(self) -> None:
        tool_num_per_type = [1, 1, 1]
        proc_time = [[1, 2, 3], [3, 2, 1], [4, 1, 1]]
        tool_type_seq = [[1, 2, 3], [3, 2, 1], [2, 1, 3]]
        num_job = 3
        num_tool_types = 3
        target_chromosome = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        OperationTypeMapping = {0: "flow", 1: "flow", 2: "flow"}

        result, _ = prepare_gannt_data_from(
            tool_num_per_type,
            proc_time,
            tool_type_seq,
            num_job,
            num_tool_types,
            target_chromosome,
            OperationTypeMapping,
        )

        # 各ジョブの終了時刻
        assert result == {0: 6, 1: 12, 2: 17}
