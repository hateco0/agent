import subprocess

from voice_os_agent.executors.base import ExecutionResult
from voice_os_agent.executors.files import FilesExecutor
from voice_os_agent.executors.shell import ShellExecutor
from voice_os_agent.executors.system import SystemExecutor
from voice_os_agent.nlu.intents import Intent, IntentType


class FakeCompleted:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _capture_run(monkeypatch, returncode: int = 0):
    calls: list[list[str]] = []

    def fake_run(args, *positional, **keyword):
        calls.append(list(args) if isinstance(args, (list, tuple)) else [args])
        return FakeCompleted(returncode=returncode)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_shutdown_command(monkeypatch):
    calls = _capture_run(monkeypatch)
    result = SystemExecutor().execute(Intent(type=IntentType.SHUTDOWN))
    assert result.success
    assert calls == [["shutdown", "/s", "/t", "60"]]


def test_restart_command(monkeypatch):
    calls = _capture_run(monkeypatch)
    result = SystemExecutor().execute(Intent(type=IntentType.RESTART))
    assert result.success
    assert calls == [["shutdown", "/r", "/t", "60"]]


def test_sleep_command(monkeypatch):
    calls = _capture_run(monkeypatch)
    result = SystemExecutor().execute(Intent(type=IntentType.SLEEP))
    assert result.success
    assert calls == [["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]]


def test_lock_command(monkeypatch):
    calls = _capture_run(monkeypatch)
    result = SystemExecutor().execute(Intent(type=IntentType.LOCK))
    assert result.success
    assert calls == [["rundll32.exe", "user32.dll,LockWorkStation"]]


def test_cancel_power_command(monkeypatch):
    calls = _capture_run(monkeypatch)
    result = SystemExecutor().execute(Intent(type=IntentType.CANCEL_POWER))
    assert result.success
    assert calls == [["shutdown", "/a"]]


def test_shell_executor_returns_output(monkeypatch):
    calls = _capture_run(monkeypatch)
    result = ShellExecutor().execute(Intent(type=IntentType.SHELL_COMMAND, entities={"command": "ipconfig"}))
    assert isinstance(result, ExecutionResult)
    assert calls == [["ipconfig"]]


def test_files_executor_known_folder():
    intent = Intent(type=IntentType.OPEN_PATH, entities={"path": "рабочий стол"})
    result = FilesExecutor().execute(intent)
    assert result.success


def test_files_executor_missing_path():
    intent = Intent(type=IntentType.OPEN_PATH, entities={"path": "нет/такой/папки"})
    result = FilesExecutor().execute(intent)
    assert not result.success
    assert "не найден" in result.message
