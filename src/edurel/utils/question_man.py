"""Question manager for managing sets of questions from text files."""

from pathlib import Path
from typing import List, Tuple, Union


class QMan:
    """Manager for question sets stored in text files.

    File format:
    - First non-empty line: "---db:" followed by database name
    - Questions start with "---tag:" followed by tag text
    - Question content follows until next tag or EOF
    - Empty lines can appear throughout
    """

    def __init__(self, qpath: Union[str, Path]):
        """Initialize QMan by parsing questions file.

        Args:
            qpath: Path to the file containing questions
        """
        self.qpath = Path(qpath)
        self.dbname = None
        self.questions: List[Tuple[str, str]] = []  # List of (tag, question) tuples
        self._parse_file()

    def _parse_file(self):
        """Parse the questions file and store questions with tags."""
        with open(self.qpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Skip empty lines and find database name
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line:
                if line.startswith('---db:'):
                    self.dbname = line[6:].strip()
                    i += 1
                    break
            i += 1

        # Parse questions
        current_tag = None
        current_question_lines = []

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.startswith('---tag:'):
                # Save previous question if exists
                if current_tag is not None:
                    question_text = ''.join(current_question_lines).strip()
                    self.questions.append((current_tag, question_text))

                # Start new question
                current_tag = stripped[7:].strip()
                current_question_lines = []
            else:
                # Accumulate question lines
                current_question_lines.append(line)

            i += 1

        # Save last question
        if current_tag is not None:
            question_text = ''.join(current_question_lines).strip()
            self.questions.append((current_tag, question_text))

    def by_tag(self, tag: str) -> List[str]:
        """Get all questions with the specified tag.

        Args:
            tag: The tag to filter by

        Returns:
            List of question texts matching the tag
        """
        return [q for t, q in self.questions if t == tag]

    def by_tags(self, tags: List[str]) -> List[Tuple[str, str]]:
        """Get all questions with any of the specified tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of (tag, question) tuples matching any of the tags
        """
        tag_set = set(tags)
        return [(t, q) for t, q in self.questions if t in tag_set]

    def by_index(
        self,
        index: Union[int, List[int], slice, List[slice]]
    ) -> List[Tuple[str, str]]:
        """Get questions by index, list of indexes, slice, or list of slices.

        Args:
            index: Single index, list of indexes, slice, or list of slices

        Returns:
            List of (tag, question) tuples
        """
        if isinstance(index, int):
            # Single index
            return [self.questions[index]]
        elif isinstance(index, slice):
            # Single slice
            return self.questions[index]
        elif isinstance(index, list):
            # List of indexes or slices
            result = []
            for idx in index:
                if isinstance(idx, int):
                    result.append(self.questions[idx])
                elif isinstance(idx, slice):
                    result.extend(self.questions[idx])
            return result
        else:
            raise TypeError(
                f"Index must be int, list of ints, slice, or list of slices, "
                f"got {type(index)}"
            )

    def get_all_tags(self) -> List[str]:
        """Get all unique tags in order of first appearance.

        Returns:
            List of unique tags
        """
        seen = set()
        tags = []
        for tag, _ in self.questions:
            if tag not in seen:
                seen.add(tag)
                tags.append(tag)
        return tags

    def __len__(self) -> int:
        """Return the number of questions."""
        return len(self.questions)

    def __getitem__(self, index: Union[int, slice]) -> Union[Tuple[str, str], List[Tuple[str, str]]]:
        """Support indexing and slicing using [] operator."""
        if isinstance(index, int):
            return self.questions[index]
        elif isinstance(index, slice):
            return self.questions[index]
        else:
            raise TypeError(f"Index must be int or slice, got {type(index)}")
