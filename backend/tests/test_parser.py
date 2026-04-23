import unittest
from app.infrastructure.ai.parser import parse_transcript_html


class TestParser(unittest.TestCase):
    def test_parse_simple_html(self):
        html = """
        <table class="commonTable">
            <tr><td>1</td><td>Math</td><td>6.0</td><td>85.0</td></tr>
            <tr><td>2</td><td>Physics</td><td>6.0</td><td>90.0</td></tr>
        </table>
        """
        entries = parse_transcript_html(html)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].subject_name, "Math")
        self.assertEqual(entries[0].mark, 85.0)

    def test_parse_empty_html(self):
        entries = parse_transcript_html("<html><body>No data</body></html>")
        self.assertEqual(len(entries), 0)


if __name__ == "__main__":
    unittest.main()
