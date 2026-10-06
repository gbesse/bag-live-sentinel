from pathlib import Path
import tempfile
import unittest

from bag_live_sentinel import probe_files, watch


class Clock:
    def __init__(self):
        self.now = 0.0

    def sleep(self, seconds):
        self.now += seconds


class SentinelTests(unittest.TestCase):
    def setUp(self):
        self.config = {"bag_dir": "/unused", "bag_glob": "*.mcap", "heartbeat_file": "/unused.heartbeat", "duration_s": 3, "sample_interval_s": 1, "max_stall_s": 1.5, "heartbeat_recent_s": 1, "warmup_s": 0}

    def test_healthy_progress_three_languages(self):
        for locale in ("fr", "en", "es"):
            clock = Clock()
            report = watch(self.config, locale, probe=lambda: (int(clock.now), int(clock.now) * 10), clock=lambda: clock.now, sleep=clock.sleep)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["bag_growth_events"], 3)

    def test_stall_while_topic_active_fails(self):
        clock = Clock()
        report = watch(self.config, probe=lambda: (int(clock.now), min(int(clock.now), 1) * 10), clock=lambda: clock.now, sleep=clock.sleep)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["findings"][0]["code"], "stalled")

    def test_no_topic_evidence_is_inconclusive(self):
        clock = Clock()
        report = watch(self.config, probe=lambda: (None, int(clock.now) * 10), clock=lambda: clock.now, sleep=clock.sleep)
        self.assertEqual(report["status"], "inconclusive")

    def test_probe_sums_split_bag_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.mcap").write_bytes(b"123")
            (root / "two.mcap").write_bytes(b"4567")
            heartbeat = root / "pulse"
            heartbeat.touch()
            config = self.config | {"bag_dir": directory, "heartbeat_file": str(heartbeat)}
            marker, total = probe_files(config)
            self.assertIsInstance(marker, int)
            self.assertEqual(total, 7)


if __name__ == "__main__":
    unittest.main()
