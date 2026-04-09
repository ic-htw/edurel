import re
from strictyaml import load, Map
from strictyaml.exceptions import YAMLValidationError


def parse_yaml(text: str, schema: Map) -> dict:
    def _format_error_location(exc: Exception) -> str | None:
        mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
        if mark is None:
            return None
    
        line = getattr(mark, "line", None)
        column = getattr(mark, "column", None)
        parts = []
        if line is not None:
            parts.append(f"line {line + 1}")
        if column is not None:
            parts.append(f"column {column + 1}")
        return ", ".join(parts) or None


    def _format_error_snippet(exc: Exception) -> str | None:
        mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
        if mark is None or not hasattr(mark, "get_snippet"):
            return None

        snippet = mark.get_snippet()
        return snippet.strip() if snippet else None


    def _build_potential_fix(problem: str, context: str) -> str:
        if "required key(s)" in problem:
            return (
                "Add the missing required field. Columns need `columnname` and `type`; "
                "tables need `tablename` and `columns`; foreign keys need "
                "`sourcecolumns`, `targettable`, and `targetcolumns`."
            )
        if "found non-matching string" in problem:
            return (
                "Check the field format against the schema. SQL types should look like "
                "`INTEGER`, `TEXT`, `VARCHAR(255)`, or `DECIMAL(9, 2)`."
            )
        if "expected <block end>" in problem or "while parsing a block" in context:
            return (
                "Fix the YAML indentation and list nesting. Child keys must line up under "
                "their parent item, and list items must stay aligned with `-`."
            )
        return "Review the YAML structure and make sure it matches the expected schema."

    try:
        parsed = load(text, schema)
        return parsed.data
    except YAMLValidationError as exc:
        problem = getattr(exc, "problem", None) or "The YAML document does not match the schema."
        context = getattr(exc, "context", None) or "Schema validation failed."
        location = _format_error_location(exc)
        snippet = _format_error_snippet(exc)

        error_parts = ["YAML validation failed."]
        if location:
            error_parts.append(f"\nLocation: {location}.")
        error_parts.append(f"\nProblem: {problem}.")
        error_parts.append(f"\nContext: {context}.")
        if snippet:
            error_parts.append(f"\nSnippet: {snippet}")
        error_parts.append(
            f"\nPotential fix: {_build_potential_fix(problem, context)}"
        )
        raise ValueError(" ".join(error_parts)) from None
    except Exception as exc:
        problem = getattr(exc, "problem", None)
        context = getattr(exc, "context", None)
        location = _format_error_location(exc)
        snippet = _format_error_snippet(exc)

        if problem or context:
            error_parts = ["YAML parsing failed."]
            if location:
                error_parts.append(f"\nLocation: {location}.")
            if problem:
                error_parts.append(f"\nProblem: {problem}.")
            if context:
                error_parts.append(f"\nContext: {context}.")
            if snippet:
                error_parts.append(f"\nSnippet: {snippet}")
            error_parts.append(
                f"\nPotential fix: {_build_potential_fix(problem or '', context or '')}"
            )
            raise ValueError(" ".join(error_parts)) from None

        raise ValueError(
            "Unexpected error while validating YAML: "
            f"{exc.__class__.__name__}: {exc}\n"
            "Potential fix: Check that the input is valid YAML text and try again. "
            "If the problem persists, inspect custom parser code or validators."
        ) from None

def yaml_extract(md):
    """Extract YAML code from markdown text.

    Args:
        md: Markdown text containing YAML code blocks

    Returns:
        str: Extracted YAML code, or empty string if no YAML found
    """
    # First, try to extract from ```yaml ... ``` blocks
    yaml_block_pattern = r'```yaml\s*\n(.*?)\n```'
    matches = re.findall(yaml_block_pattern, md, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()

    # Also try ```yml ... ``` blocks
    yml_block_pattern = r'```yml\s*\n(.*?)\n```'
    matches = re.findall(yml_block_pattern, md, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()

    # Look for generic ``` ... ``` blocks that might contain YAML
    generic_block_pattern = r'```\s*\n(.*?)\n```'
    matches = re.findall(generic_block_pattern, md, re.DOTALL)
    if matches:
        # Return the first generic block (assume it's YAML if no language specified)
        return matches[0].strip()

    return ""
