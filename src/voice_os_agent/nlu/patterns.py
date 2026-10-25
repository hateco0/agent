from __future__ import annotations

from .intents import IntentType

PATTERN_SPECS: tuple[tuple[str, IntentType], ...] = (
    (r"^(?:открой|открыть)\s+(?:папку|каталог|директорию)\s+(?P<path>.+)$", IntentType.OPEN_PATH),
    (r"^(?:открой|открыть)\s+(?:папку|каталог|директорию)$", IntentType.UNKNOWN),
    (
        r"^(?:открой|открыть)\s+(?P<path>рабочий стол|мои документы|документы|загрузки|корзину)$",
        IntentType.OPEN_PATH,
    ),
    (r"^(?:open)\s+(?P<path>desktop|documents|downloads|recycle bin)$", IntentType.OPEN_PATH),
    (r"^(?:запусти|запустить)\s+команду\s+(?P<command>.+)$", IntentType.SHELL_COMMAND),
    (r"^(?:запусти команду|запустить команду)$", IntentType.UNKNOWN),
    (
        r"^(?:выполни|выполнить|введи)\s+"
        r"(?:команду\s+|команда\s+)?(?P<command>.+)$",
        IntentType.SHELL_COMMAND,
    ),
    (
        r"^(?:run|execute|command)\s+(?P<command>.+)$",
        IntentType.SHELL_COMMAND,
    ),
    (r"^run\s+command$", IntentType.UNKNOWN),
    (
        r"^(?:открой|открыть|запусти|запустить|включи|покажи)\s+(?:приложение\s+|программу\s+)?(?P<app>.+)$",
        IntentType.OPEN_APP,
    ),
    (r"^(?:open|launch|start)\s+(?:the\s+|app\s+)?(?P<app>.+)$", IntentType.OPEN_APP),
    (r"^(?:закрой|закрыть|заверши)(?!\s+работу)\s+(?:все\s+)?(?:приложение\s+|программу\s+)?(?P<app>.+)$", IntentType.CLOSE_APP),
    (r"^(?:убей|прибей)\s+(?P<app>.+)$", IntentType.CLOSE_APP),
    (r"^(?:close|quit)\s+(?P<app>.+)$", IntentType.CLOSE_APP),
    (
        r"^(?:поставь|установи|сделай)\s+громкость\s+(?:на\s+)?(?P<level>\d{1,3})\s*(?:процентов|%)?$",
        IntentType.SET_VOLUME,
    ),
    (r"^громкость\s+(?:на\s+)?(?P<level>\d{1,3})\s*(?:процентов|%)?$", IntentType.SET_VOLUME),
    (
        r"^(?:set|change)\s+(?:the\s+)?volume\s+(?:to\s+)?(?P<level>\d{1,3})\s*(?:percent|%)?$",
        IntentType.SET_VOLUME,
    ),
    (
        r"^(?P<direction>увеличь|повысь|прибавь|добавь|уменьши|снизи|убавь)\s+"
        r"(?:громкость|звук)(?:\s+на\s+(?P<step>\d{1,3}))?$",
        IntentType.CHANGE_VOLUME,
    ),
    (
        r"^(?P<direction>increase|raise|turn up|decrease|lower|turn down)\s+"
        r"(?:the\s+)?(?:volume|sound)(?:\s+by\s+(?P<step>\d{1,3}))?$",
        IntentType.CHANGE_VOLUME,
    ),
    (r"^(?P<mute>выключи|убери|отключи|заглуши)\s+(?:звук|громкость|аудио)$", IntentType.TOGGLE_MUTE),
    (r"^(?P<mute>включи|верни|восстанови)\s+(?:звук|громкость|аудио)$", IntentType.TOGGLE_MUTE),
    (r"^без звука$", IntentType.TOGGLE_MUTE),
    (r"^(?P<mute>mute|unmute|turn off|turn on)\s+(?:the\s+)?(?:volume|sound|audio)$", IntentType.TOGGLE_MUTE),
    (r"^(?:выключи|заверши)(?:\s+работу)?\s+(?:компьютер|пк|машину|систему|комп)$", IntentType.SHUTDOWN),
    (r"^(?:заверши|выключи) работу$", IntentType.SHUTDOWN),
    (r"^завершение работы(?:\s+компьютера)?$", IntentType.SHUTDOWN),
    (r"^(?:shut down|shutdown|power off|turn off)\s+(?:the\s+)?(?:computer|pc)$", IntentType.SHUTDOWN),
    (r"^(?:перезагрузи|перезагрузить|рестартуй)(?:\s+компьютер|\s+пк)?$", IntentType.RESTART),
    (r"^(?:reboot|restart)(?:\s+the\s+computer)?$", IntentType.RESTART),
    (r"^(?:спящий режим|усни|переведи в спящий режим|спать)$", IntentType.SLEEP),
    (r"^(?:sleep|hibernate)$", IntentType.SLEEP),
    (r"^(?:заблокируй|заблокировать)(?:\s+компьютер|\s+пк)?$", IntentType.LOCK),
    (r"^lock(?:\s+the\s+computer)?$", IntentType.LOCK),
    (r"^(?:отмена|отмени|отменить|не выключай|отбой)\S*", IntentType.CANCEL_POWER),
    (r"^cancel$", IntentType.CANCEL_POWER),
    (r"^(?:скриншот|сделай скриншот|снимок экрана|сними экран|заскринь)$", IntentType.SCREENSHOT),
    (r"^(?:screenshot|take a screenshot|capture the screen)$", IntentType.SCREENSHOT),
    (r"^(?:сверни|свернуть)(?:\s+все)?\s+окна$", IntentType.MINIMIZE_ALL),
    (r"^(?:minimize|hide)\s+(?:all\s+)?windows$", IntentType.MINIMIZE_ALL),
    (r"^(?:покажи|показать)\s+(?:рабочий стол|десктоп)$", IntentType.SHOW_DESKTOP),
    (r"^(?:show|reveal)\s+(?:the\s+)?desktop$", IntentType.SHOW_DESKTOP),
)