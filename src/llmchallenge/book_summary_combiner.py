import logging

from openai import OpenAI, OpenAIError
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BookCombinerResponse(BaseModel):
    """A response model for storing the combined summary of a book.

    Attributes:
        book_title (str): The title of the book.
        book_summary (str): The summarized content of the entire book,
                            combining all chapter summaries into a cohesive text.
    """

    book_title: str
    book_summary: str


class BookSummaryCombiner:
    """A class for combining chapter summaries into cohesive book summaries using the OpenAI API.

    This class is designed to process multiple chapter summaries for a book and generate a
    single, logically flowing summary that preserves key events, character arcs, and story progression.

    Attributes:
        client (OpenAI): The OpenAI API client for making requests.
        model (str): The OpenAI model used for generating summaries (default: "gpt-4o").
        temperature (float): The sampling temperature for controlling creativity in responses.
        max_tokens (int): The maximum token limit for the output summary.
        response_format (BaseModel): The response model format for parsing results (default: BookCombinerResponse).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 12000,
        response_format: BaseModel = BookCombinerResponse,
    ) -> None:
        """Initialize the BookSummaryCombiner with the OpenAI API key and configuration.

        Args:
            api_key (str): The OpenAI API key for authentication.
            model (str, optional): The OpenAI model to use for generating summaries (default: "gpt-4o").
            temperature (float, optional): The sampling temperature to control randomness (default: 0.7).
            max_tokens (int, optional): The maximum number of tokens allowed for the output (default: 12000).
            response_format (BaseModel, optional): The response format for parsing API results
                                                   (default: BookCombinerResponse).

        Returns:
            None
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.response_format = response_format
        logger.info("BookSummaryCombiner initialized with model: %s", model)

    def summarize_book(self, chapter_summaries: dict[str, str], book_title: str) -> BookCombinerResponse:
        """Combine chapter summaries into a single book summary.

        Args:
            chapter_summaries (dict[str, str]): Dictionary of chapter titles and summaries.
            book_title (str): Title of the book.

        Returns:
            str: Summary of the entire book.
        """
        logger.info("Starting summary for book: %s", book_title)
        combined_text = "\n\n".join(
            f"{chapter_title}: {summary}" for chapter_title, summary in chapter_summaries.items()
        )
        logger.debug("Combined chapter summaries for '%s': %s", book_title, combined_text)

        system_prompt = (
            "You summarize books based on chapter summaries, ensuring logical flow. "
            "Avoid Repetitions. Highlight Character Arcs. Tighter Transitions. Highlight Interconnections"
        )
        user_prompt = (
            f"You are a professional book summarizer. Your job is to create a concise, cohesive summary of the book "
            f"'{book_title}' based on the following chapter summaries. Ensure that the story's logical flow and key "
            f"events are preserved while maintaining readability. "
            f"Here are the chapter summaries:\n\n{combined_text}\n\n"
            "Now provide a single cohesive summary of the book:"
        )

        try:
            completions = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=self.response_format,
            )
            logger.info("Summary for book '%s' generated successfully", book_title)
            return completions.choices[0].message.parsed
        except OpenAIError as e:
            logger.error("Error summarizing book '%s': %s", book_title, str(e))
            raise

    def summarize_all_books(self, books: dict[str, dict[str, str]]) -> dict[str, str]:
        """Summarize multiple books into cohesive summaries.

        Args:
            books (dict[str, dict[str, str]]): Dictionary of books with chapter summaries.

        Returns:
            dict[str, str]: Dictionary of book titles and their summaries.
        """
        logger.info("Starting summaries for multiple books...")
        summarized_books = {}
        for book_title, chapter_summaries in books.items():
            logger.info("Processing book: '%s'", book_title)
            try:
                summarized_books[book_title] = self.summarize_book(chapter_summaries, book_title).book_summary
            except Exception as e:
                logger.error("Failed to summarize book '%s': %s", book_title, str(e))
                summarized_books[book_title] = f"Error: {str(e)}"

        logger.info("Finished summarizing all books.")
        return summarized_books
