import pytest
from unittest.mock import patch, MagicMock
from icetime.report import reporter, FullFatProgress, NoOpProgress


class TestReporter:
    @pytest.mark.unit
    def test_reporter_quiet_true(self):
        """Test that reporter returns NoOpProgress when quiet=True."""
        result = reporter(quiet=True)
        assert isinstance(result, NoOpProgress)

    @pytest.mark.unit
    def test_reporter_quiet_false(self):
        """Test that reporter returns FullFatProgress when quiet=False."""
        result = reporter(quiet=False)
        assert isinstance(result, FullFatProgress)


class TestFullFatProgress:
    @pytest.mark.unit
    def test_context_manager_enter_exit(self):
        """Test FullFatProgress context manager behavior."""
        progress = FullFatProgress()

        # Test __enter__
        with patch("icetime.report.Progress") as mock_progress_class:
            mock_progress_instance = MagicMock()
            mock_progress_class.return_value = mock_progress_instance

            result = progress.__enter__()

            # Should create Progress instance and start it
            mock_progress_class.assert_called_once()
            mock_progress_instance.start.assert_called_once()
            assert result is progress
            assert progress._progress == mock_progress_instance

    @pytest.mark.unit
    def test_context_manager_exit(self):
        """Test FullFatProgress __exit__ method."""
        progress = FullFatProgress()
        mock_progress_instance = MagicMock()
        progress._progress = mock_progress_instance

        # Test __exit__
        progress.__exit__(None, None, None)
        mock_progress_instance.stop.assert_called_once()

    @pytest.mark.unit
    def test_add_task(self):
        """Test FullFatProgress add_task method."""
        progress = FullFatProgress()
        mock_progress_instance = MagicMock()
        mock_progress_instance.add_task.return_value = 42
        progress._progress = mock_progress_instance

        result = progress.add_task(
            description="Test task", total=100, some_kwarg="value"
        )

        mock_progress_instance.add_task.assert_called_once_with(
            description="Test task", total=100, some_kwarg="value"
        )
        assert result == 42

    @pytest.mark.unit
    def test_update(self):
        """Test FullFatProgress update method."""
        progress = FullFatProgress()
        mock_progress_instance = MagicMock()
        progress._progress = mock_progress_instance

        progress.update(task_id=1, advance=1, description="Updated")

        mock_progress_instance.update.assert_called_once_with(
            1, advance=1, description="Updated"
        )

    @pytest.mark.unit
    def test_full_context_manager_usage(self):
        """Test complete context manager usage with FullFatProgress."""
        with patch("icetime.report.Progress") as mock_progress_class:
            mock_progress_instance = MagicMock()
            mock_progress_instance.add_task.return_value = 1
            mock_progress_class.return_value = mock_progress_instance

            with FullFatProgress() as progress:
                task_id = progress.add_task("Test", total=10)
                progress.update(task_id, advance=1)

            # Verify Progress was created with correct columns
            mock_progress_class.assert_called_once()
            call_args = mock_progress_class.call_args[0]
            assert len(call_args) == 3  # Three columns

            # Verify start and stop were called
            mock_progress_instance.start.assert_called_once()
            mock_progress_instance.stop.assert_called_once()

            # Verify task operations
            mock_progress_instance.add_task.assert_called_once_with("Test", total=10)
            mock_progress_instance.update.assert_called_once_with(1, advance=1)


class TestNoOpProgress:
    @pytest.mark.unit
    def test_context_manager_enter(self):
        """Test NoOpProgress __enter__ returns self."""
        progress = NoOpProgress()
        result = progress.__enter__()
        assert result is progress

    @pytest.mark.unit
    def test_context_manager_exit(self):
        """Test NoOpProgress __exit__ does nothing."""
        progress = NoOpProgress()
        # Should not raise any exceptions
        result = progress.__exit__(None, None, None)
        assert result is None

    @pytest.mark.unit
    def test_add_task_returns_zero(self):
        """Test NoOpProgress add_task always returns 0."""
        progress = NoOpProgress()

        result1 = progress.add_task()
        result2 = progress.add_task(description="Test", total=100, extra="value")

        assert result1 == 0
        assert result2 == 0

    @pytest.mark.unit
    def test_update_does_nothing(self):
        """Test NoOpProgress update method does nothing."""
        progress = NoOpProgress()

        # Should not raise any exceptions
        result = progress.update(1)
        assert result is None

        result = progress.update(1, advance=1, description="test")
        assert result is None

    @pytest.mark.unit
    def test_full_context_manager_usage(self):
        """Test complete context manager usage with NoOpProgress."""
        with NoOpProgress() as progress:
            task_id = progress.add_task("Test", total=10)
            progress.update(task_id, advance=1)

        # Should complete without any errors
        assert task_id == 0


class TestReporterIntegration:
    @pytest.mark.unit
    def test_quiet_mode_integration(self):
        """Test that quiet mode provides no-op functionality."""
        with reporter(quiet=True) as progress:
            task_id = progress.add_task("Processing", total=5)
            for i in range(5):
                progress.update(task_id, advance=1)

        # Should complete without any visual output
        assert task_id == 0

    @pytest.mark.unit
    def test_verbose_mode_integration(self):
        """Test that verbose mode creates actual progress tracking."""
        with patch("icetime.report.Progress") as mock_progress_class:
            mock_progress_instance = MagicMock()
            mock_progress_instance.add_task.return_value = 1
            mock_progress_class.return_value = mock_progress_instance

            with reporter(quiet=False) as progress:
                task_id = progress.add_task("Processing", total=5)
                progress.update(task_id, advance=1)

            # Verify rich.Progress was used
            mock_progress_class.assert_called_once()
            mock_progress_instance.start.assert_called_once()
            mock_progress_instance.stop.assert_called_once()
            mock_progress_instance.add_task.assert_called_once_with(
                "Processing", total=5
            )
            mock_progress_instance.update.assert_called_once_with(1, advance=1)

    @pytest.mark.unit
    def test_reporter_interface_consistency(self):
        """Test that both progress classes have consistent interfaces."""
        quiet_progress = reporter(quiet=True)
        verbose_progress = reporter(quiet=False)

        # Both should have the same methods
        for method_name in ["__enter__", "__exit__", "add_task", "update"]:
            assert hasattr(quiet_progress, method_name)
            assert hasattr(verbose_progress, method_name)
            assert callable(getattr(quiet_progress, method_name))
            assert callable(getattr(verbose_progress, method_name))
