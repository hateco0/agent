from __future__ import annotations

import sounddevice as sd


def list_input_devices():
    items = []
    try:
        for i, d in enumerate(sd.query_devices()):
            try:
                if d.get("max_input_channels", 0) > 0:
                    items.append({"index": i, "name": str(d.get("name", f"Device {i}"))})
            except Exception:
                continue
    except Exception:
        pass
    if not items:
        items.append({"index": None, "name": "По умолчанию"})
    return items


def list_output_devices():
    items = []
    try:
        for i, d in enumerate(sd.query_devices()):
            try:
                if d.get("max_output_channels", 0) > 0:
                    items.append({"index": i, "name": str(d.get("name", f"Device {i}"))})
            except Exception:
                continue
    except Exception:
        pass
    if not items:
        items.append({"index": None, "name": "По умолчанию"})
    return items


def get_default_input():
    try:
        idx = sd.default.device[0]
        if idx is not None and idx >= 0:
            return int(idx)
    except Exception:
        pass
    return None


def get_default_output():
    try:
        idx = sd.default.device[1]
        if idx is not None and idx >= 0:
            return int(idx)
    except Exception:
        pass
    return None


def get_default_input_name():
    try:
        idx = get_default_input()
        if idx is not None:
            devs = sd.query_devices()
            if idx < len(devs):
                return str(devs[idx].get("name", ""))
    except Exception:
        pass
    return ""


def get_default_output_name():
    try:
        idx = get_default_output()
        if idx is not None:
            devs = sd.query_devices()
            if idx < len(devs):
                return str(devs[idx].get("name", ""))
    except Exception:
        pass
    return ""

