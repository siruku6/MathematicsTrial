import pytest
from eval.exec_hist_library import ExecHist, ExecHistLibrary, ToolTypeInfo


class TestExecHistLibrary:
    @pytest.fixture(name="exec_hist_library")
    def fixture_exec_hist_library(self) -> ExecHistLibrary:
        tool_type_info = {
            "tool_1": ToolTypeInfo(setup_time=10),
            "tool_2": ToolTypeInfo(setup_time=15),
            "tool_3": ToolTypeInfo(setup_time=20),
        }
        return ExecHistLibrary(tool_type_info)

    @pytest.fixture(name="exec_hist_1")
    def fixture_exec_hist_1(self) -> ExecHist:
        return ExecHist(
            tool_type_id="tool_1",
            task_no=1,
            operation_type_id=1,
            start_time=0,
            end_time=10,
        )

    @pytest.fixture(name="exec_hist_2")
    def fixture_exec_hist_2(self) -> ExecHist:
        return ExecHist(
            tool_type_id="tool_1",
            task_no=2,
            operation_type_id=2,
            start_time=45,
            end_time=55,
        )

    @pytest.fixture(name="exec_hist_3")
    def fixture_exec_hist_3(self) -> ExecHist:
        return ExecHist(
            tool_type_id="tool_1",
            task_no=3,
            operation_type_id=3,
            start_time=20,
            end_time=30,
        )

    def test_clear(
        self,
        exec_hist_library: ExecHistLibrary,
        exec_hist_1: ExecHist,
        exec_hist_2: ExecHist,
    ) -> None:
        # Add some execution history
        exec_hist_library.add("tool_1_1", exec_hist_1)
        exec_hist_library.add("tool_1_1", exec_hist_2)

        # Clear the execution history
        exec_hist_library.clear()

        # Check if the execution history is empty
        assert len(exec_hist_library.hist) == 0

    def test_add(
        self, exec_hist_library: ExecHistLibrary, exec_hist_1: ExecHist
    ) -> None:
        # Add an execution history
        exec_hist_library.add("tool_1_1", exec_hist_1)

        # Check if the execution history is added correctly
        assert len(exec_hist_library.hist) == 1
        assert "tool_1_1" in exec_hist_library.hist
        assert exec_hist_library.hist["tool_1_1"][0]["task_no"] == 1

    def test_insert(
        self,
        exec_hist_library: ExecHistLibrary,
        exec_hist_1: ExecHist,
        exec_hist_2: ExecHist,
        exec_hist_3: ExecHist,
    ) -> None:
        # Add some execution history
        exec_hist_library.add("tool_1_1", exec_hist_1)
        exec_hist_library.add("tool_1_1", exec_hist_2)

        # Insert a new execution history
        exec_hist_library.insert("tool_1_1", 1, exec_hist_3)

        # Check if the execution history is inserted correctly
        assert len(exec_hist_library.hist["tool_1_1"]) == 3
        assert exec_hist_library.hist["tool_1_1"][1]["task_no"] == 3

    def test_search_available_margin_time(
        self,
        exec_hist_library: ExecHistLibrary,
        exec_hist_1: ExecHist,
        exec_hist_2: ExecHist,
    ) -> None:
        """
        Test one margin candidate is found
        """
        # Add some execution history
        exec_hist_library.add("tool_1_1", exec_hist_1)
        exec_hist_library.add("tool_1_1", exec_hist_2)

        # Search for available margin time
        margin_candidate = exec_hist_library.search_available_margin_time(
            "tool_1", 3, 10
        )

        # Check if the correct margin candidate is returned
        assert margin_candidate["tool_id"] == "tool_1_1"
        assert margin_candidate["index"] == 1
        assert margin_candidate["margin_time"] == 15
        assert margin_candidate["start_time"] == 20

    def test_search_available_margin_time_no_candidate(
        self,
        exec_hist_library: ExecHistLibrary,
        exec_hist_1: ExecHist,
        exec_hist_2: ExecHist,
    ) -> None:
        """
        Test no margin candidate is found
        """
        # Add some execution history
        exec_hist_library.add("tool_1_1", exec_hist_1)
        exec_hist_library.add("tool_1_1", exec_hist_2)

        # Search for available margin time with no candidate
        margin_candidate = exec_hist_library.search_available_margin_time(
            "tool_1", 3, 15
        )

        # Check if no margin candidate is returned
        assert margin_candidate is None
