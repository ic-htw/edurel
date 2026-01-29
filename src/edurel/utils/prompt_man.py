"""prompt manager for managing sets of prompts from text files."""

from pathlib import Path
from typing import List, Tuple, Union


class PromptMan:
    """Manager for prompt sets stored in text files.

    File format:
    - First non-empty line: "---db:" followed by database name
    - prompts start with "---tag:" followed by tag text
    - prompt content follows until next tag or EOF
    - Empty lines can appear throughout
    """

    def __init__(self, ppath: Union[str, Path]):
        """Initialize PromptMan by parsing prompts file.

        Args:
            ppath: Path to the file containing prompts
        """
        self.ppath = Path(ppath)
        self.dbname = None
        self.prompts: List[Tuple[str, str]] = []  # List of (tag, prompt) tuples
        self._parse_file()

    def _parse_file(self):
        """Parse the prompts file and store prompts with tags."""
        with open(self.ppath, 'r', encoding='utf-8') as f:
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

        # Parse prompts
        current_tag = None
        current_prompt_lines = []

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if stripped.startswith('---tag:'):
                # Save previous prompt if exists
                if current_tag is not None:
                    prompt_text = ''.join(current_prompt_lines).strip()
                    self.prompts.append((current_tag, prompt_text))

                # Start new prompt
                current_tag = stripped[7:].strip()
                current_prompt_lines = []
            else:
                # Accumulate prompt lines
                current_prompt_lines.append(line)

            i += 1

        # Save last prompt
        if current_tag is not None:
            prompt_text = ''.join(current_prompt_lines).strip()
            self.prompts.append((current_tag, prompt_text))

    def by_tag(self, tag: str) -> List[str]:
        """Get all prompts with the specified tag.

        Args:
            tag: The tag to filter by

        Returns:
            List of prompt texts matching the tag
        """
        return [q for t, q in self.prompts if t == tag]

    def by_tags(self, tags: List[str]) -> List[Tuple[str, str]]:
        """Get all prompts with any of the specified tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of (tag, prompt) tuples matching any of the tags
        """
        tag_set = set(tags)
        return [(t, q) for t, q in self.prompts if t in tag_set]

    def by_index(
        self,
        index: Union[int, List[int], slice, List[slice]]
    ) -> List[Tuple[str, str]]:
        """Get prompts by index, list of indexes, slice, or list of slices.

        Args:
            index: Single index, list of indexes, slice, or list of slices

        Returns:
            List of (tag, prompt) tuples
        """
        if isinstance(index, int):
            # Single index
            return [self.prompts[index]]
        elif isinstance(index, slice):
            # Single slice
            return self.prompts[index]
        elif isinstance(index, list):
            # List of indexes or slices
            result = []
            for idx in index:
                if isinstance(idx, int):
                    result.append(self.prompts[idx])
                elif isinstance(idx, slice):
                    result.extend(self.prompts[idx])
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
        for tag, _ in self.prompts:
            if tag not in seen:
                seen.add(tag)
                tags.append(tag)
        return tags

    def __len__(self) -> int:
        """Return the number of prompts."""
        return len(self.prompts)

    def __getitem__(self, index: Union[int, slice]) -> Union[Tuple[str, str], List[Tuple[str, str]]]:
        """Support indexing and slicing using [] operator."""
        if isinstance(index, int):
            return self.prompts[index]
        elif isinstance(index, slice):
            return self.prompts[index]
        else:
            raise TypeError(f"Index must be int or slice, got {type(index)}")
