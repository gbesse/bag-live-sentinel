"""Detect a stalled bag while an independently observed topic is still active."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time


MESSAGES = {
    "fr": {"stalled": "Le sujet publie mais l’enregistrement ne progresse plus", "no_heartbeat": "Aucun message du sujet observé", "no_growth": "Aucune progression du bag observée", "publisher_stopped": "Le sujet ne publie plus à la fin de la fenêtre", "input": "Entrée invalide", "summary": "{heartbeats} battement(s), {growth} progression(s) du bag"},
    "en": {"stalled": "Topic is publishing but bag recording has stopped progressing", "no_heartbeat": "No topic messages observed", "no_growth": "No bag progress observed", "publisher_stopped": "Topic is no longer publishing at the end of the window", "input": "Invalid input", "summary": "{heartbeats} heartbeat(s), {growth} bag growth event(s)"},
    "es": {"stalled": "El tema publica pero la grabación del bag dejó de avanzar", "no_heartbeat": "No se observaron mensajes del tema", "no_growth": "No se observó progreso del bag", "publisher_stopped": "El tema ya no publica al final de la ventana", "input": "Entrada no válida", "summary": "{heartbeats} latido(s), {growth} avance(s) del bag"},
}


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_config(config):
    if not isinstance(config, dict) or set(config) != {"bag_dir", "bag_glob", "heartbeat_file", "duration_s", "sample_interval_s", "max_stall_s", "heartbeat_recent_s", "warmup_s"}:
        raise ValueError("config")
    for field in ("bag_dir", "bag_glob", "heartbeat_file"):
        if not isinstance(config[field], str) or not config[field]:
            raise ValueError(field)
    for field in ("duration_s", "sample_interval_s", "max_stall_s", "heartbeat_recent_s", "warmup_s"):
        if not _number(config[field]) or config[field] < (0 if field == "warmup_s" else 0.001):
            raise ValueError(field)
    if config["sample_interval_s"] > config["duration_s"]:
        raise ValueError("sample_interval_s")
    return config


def probe_files(config):
    heartbeat = Path(config["heartbeat_file"])
    try:
        marker = heartbeat.stat().st_mtime_ns
    except FileNotFoundError:
        marker = None
    bag_dir = Path(config["bag_dir"])
    total = sum(path.stat().st_size for path in bag_dir.glob(config["bag_glob"]) if path.is_file())
    return marker, total


def _finding(locale, code, elapsed_s):
    return {"code": code, "elapsed_s": round(elapsed_s, 3), "message": MESSAGES[locale][code]}


def watch(config, locale="en", *, probe=None, clock=None, sleep=None):
    if locale not in MESSAGES:
        raise ValueError("locale")
    validate_config(config)
    probe = probe or (lambda: probe_files(config))
    clock = clock or time.monotonic
    sleep = sleep or time.sleep
    start = clock()
    end = start + config["duration_s"]
    first_marker, previous_size = probe()
    if first_marker is not None and (not isinstance(first_marker, int) or isinstance(first_marker, bool)):
        raise ValueError("heartbeat marker")
    if not isinstance(previous_size, int) or previous_size < 0:
        raise ValueError("bag size")
    heartbeats = 0
    growth = 0
    last_heartbeat = None
    last_growth = start
    marker = first_marker
    current = start
    findings = []
    while current < end:
        sleep(min(config["sample_interval_s"], end - current))
        current = clock()
        observed_marker, size = probe()
        if observed_marker is not None and (not isinstance(observed_marker, int) or isinstance(observed_marker, bool)):
            raise ValueError("heartbeat marker")
        if not isinstance(size, int) or size < 0:
            raise ValueError("bag size")
        if observed_marker is not None and observed_marker != marker:
            heartbeats += 1
            last_heartbeat = current
        marker = observed_marker
        if size > previous_size:
            growth += 1
            last_growth = current
        previous_size = size
        if current - start >= config["warmup_s"] and last_heartbeat is not None and current - last_heartbeat <= config["heartbeat_recent_s"] and current - last_growth > config["max_stall_s"]:
            findings.append(_finding(locale, "stalled", current - start))
            break
    if not findings:
        if heartbeats == 0:
            findings.append(_finding(locale, "no_heartbeat", current - start))
        if growth == 0:
            findings.append(_finding(locale, "no_growth", current - start))
        if last_heartbeat is not None and current - last_heartbeat > config["heartbeat_recent_s"]:
            findings.append(_finding(locale, "publisher_stopped", current - start))
    return {"format": "bag-live-sentinel/v1", "locale": locale, "status": "fail" if any(item["code"] == "stalled" for item in findings) else "inconclusive" if findings else "pass", "summary": MESSAGES[locale]["summary"].format(heartbeats=heartbeats, growth=growth), "elapsed_s": round(current - start, 3), "heartbeats": heartbeats, "bag_growth_events": growth, "last_bag_bytes": previous_size, "findings": findings}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Monitor bag progress / Surveiller la progression du bag / Vigilar el avance del bag")
    parser.add_argument("config")
    parser.add_argument("--locale", choices=MESSAGES, default="en")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        raw = Path(args.config).read_bytes()
        report = watch(json.loads(raw), args.locale)
        report["source"] = {"path": args.config, "sha256": hashlib.sha256(raw).hexdigest()}
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(f"{MESSAGES[args.locale]['input']}: {exc if args.locale == 'en' else type(exc).__name__}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return {"pass": 0, "fail": 1, "inconclusive": 3}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
