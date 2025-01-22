import pathlib
import unittest

from llmchallenge import WarAndPeaceSegmenter


class TestWarAndPeaceSegmenter(unittest.TestCase):
    def setUp(self) -> None:
        self.segmenter = WarAndPeaceSegmenter()
        file_path = pathlib.Path(__file__).resolve().parent.parent / "data" / "war_and_peace.txt"
        with file_path.open(encoding="utf-8") as file:
            self.text = file.read()

    def test_number_of_books(self) -> None:
        books_and_chapters = self.segmenter.segment_text(self.text)
        # There are 17 books including two epilogues
        assert len(books_and_chapters) == 17, "The number of books is incorrect"

    def test_chapter_counts(self) -> None:
        books_and_chapters = self.segmenter.segment_text(self.text)
        chapter_counts = [
            28,  # Book One
            21,  # Book Two
            19,  # Book Three
            16,  # Book Four
            22,  # Book Five
            26,  # Book Six
            13,  # Book Seven
            22,  # Book Eight
            23,  # Book Nine
            39,  # Book Ten
            34,  # Book Eleven
            16,  # Book Twelve
            19,  # Book Thirteen
            19,  # Book Fourteen
            20,  # Book Fifteen
            16,  # First Epilogue
            12,  # Second Epilogue
        ]

        for i, (_book, chapters) in enumerate(books_and_chapters.items()):
            assert len(chapters) == chapter_counts[i], f"Book {i + 1} chapter count is incorrect"

    def test_book_titles(self) -> None:
        books_and_chapters = self.segmenter.segment_text(self.text)
        expected_titles = [
            "BOOK ONE:",
            "BOOK TWO:",
            "BOOK THREE:",
            "BOOK FOUR:",
            "BOOK FIVE:",
            "BOOK SIX:",
            "BOOK SEVEN:",
            "BOOK EIGHT:",
            "BOOK NINE:",
            "BOOK TEN:",
            "BOOK ELEVEN:",
            "BOOK TWELVE:",
            "BOOK THIRTEEN:",
            "BOOK FOURTEEN:",
            "BOOK FIFTEEN:",
            "FIRST EPILOGUE:",
            "SECOND EPILOGUE",
        ]
        assert list(books_and_chapters.keys()) == expected_titles, "Book titles do not match the expected list"

    def test_total_chapters(self) -> None:
        books_and_chapters = self.segmenter.segment_text(self.text)
        total_chapters = sum(len(chapters) for chapters in books_and_chapters.values())
        assert total_chapters == 365, "The total number of chapters is incorrect"


if __name__ == "__main__":
    unittest.main()
