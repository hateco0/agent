# dail_agent (VoiceOS Agent)

Голосовой агент для управления Windows через голос/текст. GUI на CustomTkinter (`dail_agent`).

## Структура проекта

```
agent/
├── dail_agent.bat           # запуск GUI
├── run_gui.py               # точка входа GUI (sys.path + логирование)
├── core/                    # общие модули (логи, настройки, БД, аудио)
├── gui/                     # интерфейс (дашборд, настройки, логи, команды)
├── src/voice_os_agent/      # ядро агента (NLU, executors, voice, security)
├── config/config.json
├── data/agent_debug.log     # единый лог отладки
└── PLAN_DO.txt              # план доработок
```

## Запуск

```bat
dail_agent.bat
```

Или напрямую:
```bash
python run_gui.py
```

## Возможности

- Единый лог `data/agent_debug.log` (просмотр во вкладке "Логи")
- Микрофон/наушники по умолчанию из системы, тест микрофона с уровнем + "Слышать себя при проверке"
- Ollama (по умолчанию `http://127.0.0.1:11434`, модель `qwen2.5:3b-instruct`) с fallback
- Команды: `открой хром`, `закрой хром`, `открой калькулятор` и др.
- Текстовый ввод в дашборде + голосовой ввод

## Настройка

1. Установить зависимости в Python 3.15:
```bash
pip install customtkinter pystray sounddevice numpy requests pyttsx3 SpeechRecognition
```
2. Установить/запустить Ollama и скачать модель:
```bash
ollama pull qwen2.5:3b-instruct
```
3. Запустить `dail_agent.bat`

## Отладка

Все события пишутся в `data/agent_debug.log`. Вкладка "Логи" отображает его с автообновлением.

## Зависимости

- customtkinter, pystray, pillow
- sounddevice, numpy
- SpeechRecognition
- pyttsx3
- requests
- ollama (опц.)
