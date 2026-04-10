import unittest
from backend.app.parser import parse_transcript_html

class TestParser(unittest.TestCase):
    def test_parse_transcript_real_sample(self):
        # Snippet based on transcipt.html
        html = """
        <table class="commonTable">
            <tbody>
                <tr><td>1</td><td>История Казахстана</td><td class="commonCenteredTD">5</td><td class="commonCenteredTD">71.0</td><td>C+</td><td>2.33</td><td>Хорошо</td></tr>
                <tr><td>2</td><td>Культурология</td><td class="commonCenteredTD">2</td><td class="commonCenteredTD">85.0</td><td>B+</td><td>3.33</td><td>Хорошо</td></tr>
            </tbody>
        </table>
        """
        entries = parse_transcript_html(html)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].subject_name, "История Казахстана")
        self.assertEqual(entries[0].credits, 5.0)
        self.assertEqual(entries[0].mark, 71.0)
        self.assertEqual(entries[1].subject_name, "Культурология")
        self.assertEqual(entries[1].mark, 85.0)

if __name__ == '__main__':
    unittest.main()
