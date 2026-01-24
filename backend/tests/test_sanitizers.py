import unittest
from app.core.sanitizers import strip_markdown_fences

class TestSanitizers(unittest.TestCase):
    def test_strip_typst_fence(self):
        input_code = "```typst\n#let x = 1\n```"
        expected = "#let x = 1"
        self.assertEqual(strip_markdown_fences(input_code), expected)

    def test_strip_latex_fence(self):
        input_code = "```latex\n\\begin{document}\nHello\n\\end{document}\n```"
        expected = "\\begin{document}\nHello\n\\end{document}"
        self.assertEqual(strip_markdown_fences(input_code), expected)

    def test_strip_plain_fence(self):
        input_code = "```\nSome content\n```"
        expected = "Some content"
        self.assertEqual(strip_markdown_fences(input_code), expected)

    def test_idempotency(self):
        input_code = "Content without fences"
        first_pass = strip_markdown_fences(input_code)
        second_pass = strip_markdown_fences(first_pass)
        self.assertEqual(first_pass, second_pass)
        self.assertEqual(first_pass, input_code)

    def test_whitespace_handling(self):
        input_code = "  \n```latex\nContent\n```  \n"
        expected = "Content"
        self.assertEqual(strip_markdown_fences(input_code), expected)

    def test_empty_input(self):
        self.assertEqual(strip_markdown_fences(""), "")
        self.assertEqual(strip_markdown_fences(None), "")

if __name__ == '__main__':
    unittest.main()
