import logging

from openai import OpenAI, OpenAIError
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ChapterSummaryResponse(BaseModel):
    """Represents a response containing a chapter summary.

    Attributes:
        book_title (str): The title of the book.
        chapter_title (str): The title of the chapter.
        chapter_summary (str): The summary of the chapter.
    """

    book_title: str
    chapter_title: str
    chapter_summary: str


class ChapterSummarizer:
    """A utility class to summarize chapters of books using the OpenAI API.

    This class facilitates summarizing individual chapters of books,
    combining chapter summaries into book summaries, and handling
    OpenAI API communication for text summarization tasks.

    Attributes:
        client (OpenAI): An OpenAI client instance for API interaction.
        model (str): The OpenAI model to use for summarization (default: "gpt-4o").
        temperature (float): The temperature setting for the LLM (default: 0.7).
        max_tokens (int): The maximum number of tokens for each API response (default: 300).
        response_format (BaseModel): The response format for parsing the API response.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 300,
        response_format: BaseModel = ChapterSummaryResponse,
    ) -> None:
        """Initialize the ChapterSummarizer with the OpenAI API key and model.

        Args:
            api_key (str): OpenAI API key.
            model (str): OpenAI model to use (default: "gpt-4o").
            temperature (float): Temprature for the llm
            max_tokens (int): Max tokens for the output
            response_format (BaseModel): the response format of the query
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.response_format = response_format
        logger.info("Initialized ChapterSummarizer with model: %s", model)

    def summarize_chapter(self, book_title: str, chapter_title: str, chapter_text: str) -> ChapterSummaryResponse:
        """Summarize a single chapter using the OpenAI API.

        Args:
            book_title (str): Title of the book.
            chapter_title (str): Title of the chapter.
            chapter_text (str): Content of the chapter.

        Returns:
            str: Summarized chapter content.
        """
        system_prompt = (
            "You are a helpful assistant trained to summarize books chapter by chapter. "
            "Each summary should be concise and capture the main points, important events, and key takeaways. "
            "Make sure to provide enough context to understand the chapter without needing the full text."
        )
        user_prompt = (
            f"Summarize the following chapter from the book '{book_title}'. "
            f"The chapter is titled '{chapter_title}'. Ensure the summary is no longer than 200 words:\n\n{chapter_text}"
        )

        try:
            logger.info("Summarizing chapter '%s' from book '%s'.", chapter_title, book_title)
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=self.response_format,
            )
            logger.info("Successfully summarized chapter '%s'.", chapter_title)
            return completion.choices[0].message.parsed
        except OpenAIError as e:
            logger.error("Error summarizing chapter '%s': %s", chapter_title, e)
            raise

    def summarize_books_and_chapters(self, books: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
        """Summarize all chapters in all books.

        Args:
            books (Dict[str, Dict[str, str]]): A nested dictionary with book titles as keys
                                               and chapters (as dicts) as values.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary with the same structure, but with chapter summaries instead of full content.
        """
        summaries = {}

        for book_title, chapters in books.items():
            logger.info("Starting summarization for book: '%s'.", book_title)
            summaries[book_title] = {}
            for chapter_title, chapter_text in chapters.items():
                logger.info("Processing chapter: '%s'.", chapter_title)
                try:
                    summary = self.summarize_chapter(book_title, chapter_title, chapter_text)
                    summaries[book_title][chapter_title] = summary.chapter_summary
                except OpenAIError as e:
                    logger.error("Failed to summarize chapter '%s' from book '%s': %s", chapter_title, book_title, e)
                    summaries[book_title][chapter_title] = f"Error: {e}"

        logger.info("Completed summarization for all books.")
        return summaries
