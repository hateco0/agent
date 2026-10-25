from voice_os_agent.core.agent import VoiceAgent
from voice_os_agent.core.settings import SecuritySettings
from voice_os_agent.executors.base import BaseExecutor, ExecutionResult, ExecutorRegistry
from voice_os_agent.nlu.intents import Intent, IntentType
from voice_os_agent.nlu.parser import IntentParser
from voice_os_agent.security.guard import SecurityGuard


class DummyExecutor(BaseExecutor):
    handled = frozenset({IntentType.SHUTDOWN, IntentType.OPEN_APP})

    def __init__(self):
        self.executed = []

    def execute(self, intent: Intent) -> ExecutionResult:
        self.executed.append(intent.type)
        return ExecutionResult(success=True, message="done")


def make_agent(confirm_dangerous: bool = True):
    registry = ExecutorRegistry()
    dummy = DummyExecutor()
    registry.register(dummy)
    guard = SecurityGuard(SecuritySettings(confirm_dangerous=confirm_dangerous))
    return VoiceAgent(IntentParser(), registry, guard), dummy


def test_shutdown_requires_confirmation():
    agent, dummy = make_agent()
    result = agent.handle("выключи компьютер")
    assert result.needs_confirmation
    assert dummy.executed == []

    confirmed = agent.handle("да")
    assert confirmed.success
    assert dummy.executed == [IntentType.SHUTDOWN]


def test_shutdown_cancel():
    agent, dummy = make_agent()
    agent.handle("выключи компьютер")
    cancelled = agent.handle("нет")
    assert cancelled.success
    assert dummy.executed == []


def test_shell_command_blocked():
    agent, _ = make_agent()
    result = agent.handle("выполни format c:")
    assert result.success is False
    assert "запрещена" in result.message


def test_shell_command_chaining_blocked():
    agent, _ = make_agent()
    result = agent.handle("выполни ipconfig & format c:")
    assert result.success is False
    assert "запрещена" in result.message


def test_unknown_command():
    agent, _ = make_agent()
    result = agent.handle("расскажи анекдот")
    assert result.success is False
