from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from claude_usage.notifications import NotificationMarkers
from claude_usage.display import StatusIconRenderer
import xml.etree.ElementTree as ET
from claude_usage.usage import (
    display_snapshots,
    parse_limits,
    plan_display_name,
    reset_countdown,
    snapshot_heading,
    window_label,
    warning_threshold,
)


class UsageTests(unittest.TestCase):
    def test_warning_thresholds(self) -> None:
        cases = ((25, None), (20, 20), (15, 20), (10, 10), (7, 10), (5, 5), (1, 5))
        for remaining, expected in cases:
            with self.subTest(remaining=remaining):
                self.assertEqual(warning_threshold(remaining), expected)

    def test_multi_bucket_fixture_matches_expected_shape(self) -> None:
        fixture = {
            "rateLimitsByLimitId": {
                "claude_opus": {
                    "limitName": "Opus limit",
                    "primary": {
                        "usedPercent": 1,
                        "windowDurationMins": 10_080,
                        "resetsAt": 2_000_000,
                    },
                },
                "claude": {
                    "planType": "max",
                    "primary": {
                        "usedPercent": 20,
                        "windowDurationMins": 300,
                        "resetsAt": 1_500_000,
                    },
                    "secondary": {
                        "usedPercent": 89,
                        "windowDurationMins": 10_080,
                        "resetsAt": 2_000_000,
                    },
                },
            }
        }
        displayed = display_snapshots(parse_limits(fixture))
        self.assertEqual([item.id for item in displayed], ["claude.primary", "claude.secondary"])
        self.assertEqual([item.window_minutes for item in displayed], [300, 10_080])
        self.assertEqual([item.remaining_percent for item in displayed], [80, 11])
        self.assertTrue(all(item.plan_type == "max" for item in displayed))
        self.assertEqual(
            displayed[0].resets_at,
            datetime.fromtimestamp(1_500_000, tz=timezone.utc),
        )

    def test_legacy_single_bucket_response(self) -> None:
        snapshots = parse_limits(
            {"rateLimits": {"primary": {"usedPercent": 40, "windowDurationMins": 60}}}
        )
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].remaining_percent, 60)
        self.assertEqual(snapshots[0].limit_id, "claude")

    def test_plan_names(self) -> None:
        self.assertEqual(plan_display_name("pro"), "Pro")
        self.assertEqual(plan_display_name("max"), "Max")
        self.assertEqual(plan_display_name("team"), "Team")
        self.assertEqual(plan_display_name("enterprise"), "Enterprise")
        self.assertIsNone(plan_display_name("future_internal_plan"))

    def test_display_formatting(self) -> None:
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(window_label(300), "Session limit")
        self.assertEqual(window_label(10_080), "Weekly limit")
        self.assertEqual(
            reset_countdown(now + timedelta(days=4, hours=7), now),
            "Resets in 4 days 7 hours",
        )
        snapshot = parse_limits(
            {
                "rateLimits": {
                    "planType": "pro",
                    "primary": {"usedPercent": 40, "windowDurationMins": 300},
                }
            }
        )[0]
        self.assertEqual(snapshot_heading(snapshot), "Claude · Pro · Session limit")

    def test_notification_is_recorded_once_per_reset_window(self) -> None:
        snapshot = parse_limits(
            {
                "rateLimits": {
                    "primary": {
                        "usedPercent": 85,
                        "windowDurationMins": 300,
                        "resetsAt": 2_000_000,
                    }
                }
            }
        )[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notifications.json"
            markers = NotificationMarkers(path)
            self.assertTrue(markers.should_notify(snapshot))
            self.assertFalse(markers.should_notify(snapshot))
            self.assertFalse(NotificationMarkers(path).should_notify(snapshot))

    def test_ring_icons_cover_empty_partial_and_full_remaining_limits(self) -> None:
        ns = {"svg": "http://www.w3.org/2000/svg"}
        with tempfile.TemporaryDirectory() as directory:
            renderer = StatusIconRenderer(Path(directory))
            empty = ET.parse(renderer.render(None, 0))
            self.assertEqual(len(empty.findall(".//svg:circle", ns)), 2)
            self.assertEqual(len(empty.findall(".//svg:path", ns)), 0)
            partial = ET.parse(renderer.render(75, 40))
            arcs = partial.findall(".//svg:path", ns)
            self.assertEqual(len(arcs), 2)
            self.assertEqual(arcs[0].get("stroke"), "#D97757")
            self.assertEqual(arcs[1].get("stroke"), "#F0B48A")
            self.assertIn("A 28 28 0 1 1", arcs[0].get("d"))
            self.assertIn("A 21.5 21.5 0 0 1", arcs[1].get("d"))
            self.assertEqual(partial.findall(".//svg:text", ns), [])
            full = ET.parse(renderer.render(100, 100))
            self.assertEqual(len(full.findall(".//svg:circle", ns)), 4)
            self.assertEqual(renderer.render(-10, 120), renderer.render(0, 100))
            weekly_only = ET.parse(renderer.render(None, 40))
            arcs = weekly_only.findall(".//svg:path", ns)
            self.assertEqual(len(arcs), 1)
            self.assertEqual(arcs[0].get("stroke"), "#F0B48A")


if __name__ == "__main__":
    unittest.main()
