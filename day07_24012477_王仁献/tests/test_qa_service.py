import unittest
from pathlib import Path

from services.qa_service import answer_question


BASE_DIR = Path(__file__).resolve().parent.parent


class AnswerQuestionTests(unittest.TestCase):
    def test_unsupported_question_returns_friendly_message(self):
        answer = answer_question(BASE_DIR, "今天的天气怎么样？")
        self.assertIn("暂时无法回答", answer)
        self.assertIn("用户数", answer)


if __name__ == "__main__":
    unittest.main()
