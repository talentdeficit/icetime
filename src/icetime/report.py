from rich.progress import Progress, SpinnerColumn, TextColumn, MofNCompleteColumn


def reporter(quiet: bool) -> Progress:
    """Return a progress bar or a no-op based on the quiet flag."""
    if quiet:
        return NoOpProgress()
    else:
        return FullFatProgress()


class FullFatProgress:
    """Progress class that uses rich.Progress for detailed output"""

    def __enter__(self):
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            MofNCompleteColumn(),
        )
        self._progress.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._progress.stop()

    def add_task(self, *args, **kwargs):
        return self._progress.add_task(*args, **kwargs)

    def update(self, task_id, **kwargs):
        self._progress.update(task_id, **kwargs)


class NoOpProgress:
    """Progress class that does nothing - same interface as rich.Progress"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_task(self, description=None, total=None, **kwargs):
        return 0

    def update(self, task_id, **kwargs):
        pass
