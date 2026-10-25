from voice_os_agent.nlu.intents import IntentType
from voice_os_agent.nlu.parser import IntentParser


def make_parser():
    return IntentParser()


def test_open_app_ru():
    intent = make_parser().parse("Открой браузер!")
    assert intent.type is IntentType.OPEN_APP
    assert intent.entities["app"] == "браузер"


def test_open_app_en():
    intent = make_parser().parse("open notepad")
    assert intent.type is IntentType.OPEN_APP
    assert intent.entities["app"] == "notepad"


def test_open_folder():
    intent = make_parser().parse("открой папку загрузки")
    assert intent.type is IntentType.OPEN_PATH
    assert intent.entities["path"] == "загрузки"


def test_set_volume():
    intent = make_parser().parse("поставь громкость на 40 процентов")
    assert intent.type is IntentType.SET_VOLUME
    assert intent.entities["level"] == "40"


def test_change_volume_down():
    intent = make_parser().parse("уменьши громкость на 15")
    assert intent.type is IntentType.CHANGE_VOLUME
    assert intent.entities["direction"] == "уменьши"
    assert intent.entities["step"] == "15"


def test_mute():
    intent = make_parser().parse("выключи звук")
    assert intent.type is IntentType.TOGGLE_MUTE


def test_shutdown():
    intent = make_parser().parse("выключи компьютер")
    assert intent.type is IntentType.SHUTDOWN


def test_screenshot():
    intent = make_parser().parse("сделай скриншот")
    assert intent.type is IntentType.SCREENSHOT


def test_shell_command():
    intent = make_parser().parse("выполни ipconfig")
    assert intent.type is IntentType.SHELL_COMMAND
    assert intent.entities["command"] == "ipconfig"


def test_shell_command_with_command_word():
    intent = make_parser().parse("запусти команду ipconfig")
    assert intent.type is IntentType.SHELL_COMMAND
    assert intent.entities["command"] == "ipconfig"


def test_shell_command_without_command_word():
    intent = make_parser().parse("запусти команду")
    assert intent.type is IntentType.UNKNOWN



def test_cancel_power():
    intent = make_parser().parse("отмена")
    assert intent.type is IntentType.CANCEL_POWER


def test_open_app_infinitive():
    intent = make_parser().parse("открыть блокнот")
    assert intent.type is IntentType.OPEN_APP
    assert intent.entities["app"] == "блокнот"


def test_shutdown_work_phrase():
    intent = make_parser().parse("заверши работу")
    assert intent.type is IntentType.SHUTDOWN


def test_show_desktop():
    intent = make_parser().parse("покажи рабочий стол")
    assert intent.type in (IntentType.SHOW_DESKTOP, IntentType.OPEN_APP, IntentType.OPEN_PATH)


def test_unknown():
    intent = make_parser().parse("какая погода сегодня")
    assert intent.type is IntentType.UNKNOWN