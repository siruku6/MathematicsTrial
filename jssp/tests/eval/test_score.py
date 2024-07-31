import numpy as np
import pytest
from jssp.eval.exec_hist_library import ExecHistLibrary, ToolTypeInfo
from jssp.eval.score import calc_time4job, prepare_gannt_data_from


@pytest.fixture(name="small_proc_time")
def fixture_small_proc_time() -> list[list[int]]:
    return [[1, 2, 3], [3, 2, 1], [4, 1, 1]]


@pytest.fixture(name="small_tool_type_seq")
def fixture_small_tool_type_seq() -> list[list[int]]:
    return [[1, 2, 3], [3, 2, 1], [2, 1, 3]]


class TestCalcTime4Job:
    def test_all_flow_jobs(
        self, small_proc_time: list[list[int]], small_tool_type_seq: list[list[int]]
    ) -> None:
        tool_num_per_type = [1, 1, 1]
        num_tool_types = np.array(small_proc_time).shape[0]
        num_job = np.array(small_proc_time).shape[1]
        target_chromosome = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        OperationTypeMapping = {0: "flow", 1: "flow", 2: "flow"}

        result = calc_time4job(
            tool_num_per_type,
            small_proc_time,
            small_tool_type_seq,
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
    def test_all_flow_jobs(
        self, small_proc_time: list[list[int]], small_tool_type_seq: list[list[int]]
    ) -> None:
        tool_num_per_type = [1, 1, 1]
        num_tool_types = np.array(small_proc_time).shape[0]
        num_job = np.array(small_proc_time).shape[1]
        target_chromosome = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        OperationTypeMapping = {0: "flow", 1: "flow", 2: "flow"}

        result, _, _ = prepare_gannt_data_from(
            tool_num_per_type,
            small_proc_time,
            small_tool_type_seq,
            num_job,
            num_tool_types,
            target_chromosome,
            OperationTypeMapping,
        )

        # 各ジョブの終了時刻
        assert result == {0: 6, 1: 12, 2: 17}

    @pytest.fixture(name="exec_hist_library")
    def fixture_exec_hist_library(self) -> ExecHistLibrary:
        tool_type_info = {
            "tool_1": ToolTypeInfo(setup_time=5),
            "tool_2": ToolTypeInfo(setup_time=10),
            "tool_3": ToolTypeInfo(setup_time=15),
        }
        return ExecHistLibrary(tool_type_info)

    def test_with_cleared_hist_lib(self, exec_hist_library: ExecHistLibrary) -> None:
        tool_num_per_type = [1, 1, 1]
        proc_time = [[10, 25, 5], [35, 3, 40], [35, 5, 10]]
        tool_type_seq = [[1, 2, 3], [3, 2, 1], [2, 1, 3]]
        num_job = 3
        num_tool_types = 3
        target_chromosome = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        OperationTypeMapping = {0: "flow", 1: "flow", 2: "open"}

        make_span_per_job, _, lib_result = prepare_gannt_data_from(
            tool_num_per_type,
            proc_time,
            tool_type_seq,
            num_job,
            num_tool_types,
            target_chromosome,
            OperationTypeMapping,
            hist_lib=exec_hist_library,
            clear=True,
        )

        assert lib_result.hist == {}

    @pytest.fixture(name="expected_hist")
    def fixture_expected_hist(self) -> dict:
        return {
            "tool_1_0": [
                {
                    "tool_type_id": "tool_1",
                    "operation_type_id": 0,
                    "task_no": 0,
                    "start_time": 0,
                    "end_time": 10,
                },
                {
                    "tool_type_id": "tool_1",
                    "operation_type_id": 2,
                    "task_no": 1,
                    "start_time": 15,
                    "end_time": 20,
                },
                {
                    "tool_type_id": "tool_1",
                    "operation_type_id": 1,
                    "task_no": 2,
                    "start_time": 78,
                    "end_time": 118,
                },
            ],
            "tool_2_0": [
                {
                    "tool_type_id": "tool_2",
                    "operation_type_id": 0,
                    "task_no": 1,
                    "start_time": 10,
                    "end_time": 35,
                },
                {
                    "tool_type_id": "tool_2",
                    "operation_type_id": 1,
                    "task_no": 1,
                    "start_time": 75,
                    "end_time": 78,
                },
                {
                    "tool_type_id": "tool_2",
                    "operation_type_id": 2,
                    "task_no": 0,
                    "start_time": 78,
                    "end_time": 113,
                },
            ],
            "tool_3_0": [
                {
                    "tool_type_id": "tool_3",
                    "operation_type_id": 0,
                    "task_no": 2,
                    "start_time": 35,
                    "end_time": 40,
                },
                {
                    "tool_type_id": "tool_3",
                    "operation_type_id": 1,
                    "task_no": 0,
                    "start_time": 40,
                    "end_time": 75,
                },
                {
                    "tool_type_id": "tool_3",
                    "operation_type_id": 2,
                    "task_no": 2,
                    "start_time": 113,
                    "end_time": 123,
                },
            ],
        }

    def test_with_hist_lib(
        self, exec_hist_library: ExecHistLibrary, expected_hist: dict
    ) -> None:
        tool_num_per_type = [1, 1, 1]
        proc_time = [[10, 25, 5], [35, 3, 40], [35, 5, 10]]
        tool_type_seq = [[1, 2, 3], [3, 2, 1], [2, 1, 3]]
        num_job = 3
        num_tool_types = 3
        target_chromosome = [0, 0, 0, 1, 1, 1, 2, 2, 2]
        OperationTypeMapping = {0: "flow", 1: "flow", 2: "open"}

        make_span_per_job, _, lib_result = prepare_gannt_data_from(
            tool_num_per_type,
            proc_time,
            tool_type_seq,
            num_job,
            num_tool_types,
            target_chromosome,
            OperationTypeMapping,
            hist_lib=exec_hist_library,
            clear=False,
        )

        assert lib_result.hist == expected_hist

        # make_span_per_job の一致判定
        assert make_span_per_job == {0: 40, 1: 118, 2: 123}
