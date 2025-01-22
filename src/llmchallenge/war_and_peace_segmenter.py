import logging
import re

# Set up the logger for this module
logger = logging.getLogger(__name__)

BOOK_PATTERN = r"(BOOK\s+\w+:.*?|FIRST\s+EPILOGUE:.*?|SECOND\s+EPILOGUE.*)"
CHAPTER_PATTERN = r"(CHAPTER\s+\w+)"
CLEANUP_MARKER = r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK WAR AND PEACE \*\*\*"


class WarAndPeaceSegmenter:
    """A class for segmenting text into books and chapters using customizable patterns and a cleanup marker."""

    def __init__(
        self,
        book_pattern: str = BOOK_PATTERN,
        chapter_pattern: str = CHAPTER_PATTERN,
        cleanup_marker: str = CLEANUP_MARKER,
    ) -> None:
        """Initializes the TextSegmenter with patterns for books, chapters, and a cleanup marker.

        Args:
            book_pattern (str): Regex pattern to match book titles.
            chapter_pattern (str): Regex pattern to match chapter titles.
            cleanup_marker (str): Marker to remove text beyond a certain point.
        """
        logger.info("Initializing WarAndPeaceSegmenter")
        self.book_pattern = book_pattern
        self.chapter_pattern = chapter_pattern
        self.cleanup_marker = cleanup_marker
        logger.debug(
            "Initialized with book_pattern='%s', chapter_pattern='%s', cleanup_marker='%s'",
            book_pattern,
            chapter_pattern,
            cleanup_marker,
        )

    def clean_text(self, text: str) -> str:
        """Removes text after the cleanup marker.

        Args:
            text (str): The input text to clean.

        Returns:
            str: Cleaned text with content after the marker removed.
        """
        logger.info("Cleaning text using cleanup marker")
        logger.debug("Original text length: %d", len(text))
        cleaned_text = re.sub(f"{self.cleanup_marker}.*", "", text, flags=re.DOTALL)
        logger.debug("Cleaned text length: %d", len(cleaned_text))
        return cleaned_text

    def segment_text(self, text: str) -> dict[str, dict[str, str]]:
        """Segments text into books and chapters based on the provided patterns.

        Args:
            text (str): The input text to segment.

        Returns:
            dict: A dictionary where keys are book titles, and values are dictionaries of chapter titles and their content.
        """
        logger.info("Segmenting text into books and chapters")
        # Clean the text using the marker
        text = self.clean_text(text)

        # Split the text into books
        logger.debug("Splitting text into books using book_pattern")
        books = re.split(self.book_pattern, text)
        logger.debug("Found %d book sections", len(books) // 2)

        segmented_books = {}
        for i in range(1, len(books), 2):  # Skip odd indices since they contain book titles
            book_title = books[i].strip()
            book_content = books[i + 1].strip() if i + 1 < len(books) else ""
            logger.debug("Processing book: '%s' with content length: %d", book_title, len(book_content))

            # Split the book content into chapters
            logger.debug("Splitting book '%s' into chapters using chapter_pattern", book_title)
            chapters = re.split(self.chapter_pattern, book_content)
            logger.debug("Found %d chapter sections in book '%s'", len(chapters) // 2, book_title)

            segmented_chapters = {}
            for j in range(1, len(chapters), 2):  # Skip odd indices since they contain chapter titles
                chapter_title = chapters[j].strip()
                chapter_content = chapters[j + 1].strip() if j + 1 < len(chapters) else ""
                logger.debug("Processed chapter: '%s' with content length: %d", chapter_title, len(chapter_content))
                segmented_chapters[chapter_title] = chapter_content

            segmented_books[book_title] = segmented_chapters

        logger.info("Completed text segmentation")
        return segmented_books
