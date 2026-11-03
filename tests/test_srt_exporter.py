import tempfile
import unittest
from pathlib import Path

from srt_exporter import _fmt_time, _group_segments, export_srt, export_vtt


class TestSrtExporter(unittest.TestCase):
    def test_fmt_time_formats_hours_minutes_seconds_and_milliseconds(self):
        self.assertEqual(_fmt_time(3661.5), "01:01:01,500")

    def test_group_segments_attaches_leading_punctuation_to_previous_segment(self):
        segments = [
            {"text": "Hello", "start": 0.0, "end": 0.4},
            {"text": ".", "start": 0.4, "end": 0.5},
            {"text": "Bye", "start": 1.0, "end": 2.0},
        ]

        self.assertEqual(
            _group_segments(segments),
            [
                {"text": "Hello.", "start": 0.0, "end": 0.5},
                {"text": "Bye", "start": 1.0, "end": 2.0},
            ],
        )

    def test_group_segments_returns_empty_list_for_no_segments(self):
        self.assertEqual(_group_segments([]), [])

    def test_export_srt_writes_numbered_cues_and_returns_output_path(self):
        segments = [
            {"text": "Hello", "start": 0.0, "end": 0.4},
            {"text": ".", "start": 0.4, "end": 0.5},
            {"text": "Bye", "start": 1.0, "end": 2.0},
        ]

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "captions.srt"

            returned_path = export_srt(segments, output_path)

            self.assertEqual(returned_path, output_path)
            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "1\n"
                "00:00:00,000 --> 00:00:00,500\n"
                "Hello.\n"
                "\n"
                "2\n"
                "00:00:01,000 --> 00:00:02,000\n"
                "Bye\n",
            )

    def test_export_vtt_writes_header_and_dot_millisecond_separator(self):
        segments = [{"text": "Hello", "start": 0.0, "end": 1.234}]

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "captions.vtt"

            returned_path = export_vtt(segments, output_path)

            self.assertEqual(returned_path, output_path)
            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "WEBVTT\n"
                "\n"
                "00:00:00.000 --> 00:00:01.234\n"
                "Hello\n",
            )


if __name__ == "__main__":
    unittest.main()