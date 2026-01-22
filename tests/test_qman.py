"""Tests for QMan question manager."""

import pytest
from pathlib import Path
from edurel.utils.question_man import QMan


@pytest.fixture
def qman():
    """Create a QMan instance with the company_en.txt file."""
    qpath = Path(__file__).parent.parent / "questions" / "zzz_testset.txt"
    return QMan(qpath)


def test_init(qman):
    """Test that QMan initializes and parses the file correctly."""
    assert qman.dbname == "company_en"
    assert len(qman) > 0


def test_dbname(qman):
    """Test that database name is parsed correctly."""
    assert qman.dbname == "company_en"


def test_questions_count(qman):
    """Test that all questions are parsed."""
    # Based on company_en.txt, there should be 9 questions
    assert len(qman.questions) == 9


def test_first_question_tag(qman):
    """Test that the first question has the correct tag."""
    tag, _ = qman.questions[0]
    assert tag == "entry_year"


def test_first_question_content(qman):
    """Test that the first question content is parsed correctly."""
    _, question = qman.questions[0]
    assert "create a SQL query" in question
    assert "entry year per employee" in question
    assert "sorted by eid" in question


def test_by_tag_single_result(qman):
    """Test accessing questions by a tag with single result."""
    results = qman.by_tag("entry_year")
    assert len(results) == 1
    assert "entry year per employee" in results[0]


def test_by_tag_nonexistent(qman):
    """Test accessing questions by a non-existent tag."""
    results = qman.by_tag("nonexistent_tag")
    assert len(results) == 0


def test_by_tags_multiple(qman):
    """Test accessing questions by multiple tags."""
    results = qman.by_tags(["entry_year", "employees_without_bonus"])
    assert len(results) == 2
    tags = [tag for tag, _ in results]
    assert "entry_year" in tags
    assert "employees_without_bonus" in tags


def test_by_index_single(qman):
    """Test accessing a single question by index."""
    result = qman.by_index(0)
    assert len(result) == 1
    tag, question = result[0]
    assert tag == "entry_year"


def test_by_index_negative(qman):
    """Test accessing a question by negative index."""
    result = qman.by_index(-1)
    assert len(result) == 1
    tag, _ = result[0]
    assert tag == "employees_per_project"


def test_by_index_list_of_indexes(qman):
    """Test accessing questions by a list of indexes."""
    result = qman.by_index([0, 2, 4])
    assert len(result) == 3
    tags = [tag for tag, _ in result]
    assert tags[0] == "entry_year"
    assert tags[1] == "hireyears_department_14"
    assert tags[2] == "employees_with_bonus"


def test_by_index_slice(qman):
    """Test accessing questions by a slice."""
    result = qman.by_index(slice(0, 3))
    assert len(result) == 3
    tags = [tag for tag, _ in result]
    assert tags[0] == "entry_year"
    assert tags[1] == "entry_year_department_14"
    assert tags[2] == "hireyears_department_14"


def test_by_index_slice_with_step(qman):
    """Test accessing questions by a slice with step."""
    result = qman.by_index(slice(0, 6, 2))
    assert len(result) == 3
    tags = [tag for tag, _ in result]
    assert tags[0] == "entry_year"
    assert tags[1] == "hireyears_department_14"
    assert tags[2] == "employees_with_bonus"


def test_by_index_list_of_slices(qman):
    """Test accessing questions by a list of slices."""
    result = qman.by_index([slice(0, 2), slice(4, 6)])
    assert len(result) == 4
    tags = [tag for tag, _ in result]
    assert tags[0] == "entry_year"
    assert tags[1] == "entry_year_department_14"
    assert tags[2] == "employees_with_bonus"
    assert tags[3] == "total_income_per_employe_department_17"


def test_by_index_mixed_list(qman):
    """Test accessing questions by a mixed list of indexes and slices."""
    result = qman.by_index([0, slice(2, 4), 6])
    assert len(result) == 4
    tags = [tag for tag, _ in result]
    assert tags[0] == "entry_year"
    assert tags[1] == "hireyears_department_14"
    assert tags[2] == "employees_without_bonus"
    assert tags[3] == "salary_band_per_employee"


def test_get_all_tags(qman):
    """Test getting all unique tags."""
    tags = qman.get_all_tags()
    assert len(tags) == 9
    assert tags[0] == "entry_year"
    assert tags[-1] == "employees_per_project"


def test_len(qman):
    """Test __len__ method."""
    assert len(qman) == 9


def test_getitem_single_index(qman):
    """Test __getitem__ with single index."""
    tag, question = qman[0]
    assert tag == "entry_year"
    assert "entry year per employee" in question


def test_getitem_negative_index(qman):
    """Test __getitem__ with negative index."""
    tag, _ = qman[-1]
    assert tag == "employees_per_project"


def test_getitem_slice(qman):
    """Test __getitem__ with slice."""
    results = qman[1:4]
    assert len(results) == 3
    tags = [tag for tag, _ in results]
    assert tags[0] == "entry_year_department_14"
    assert tags[1] == "hireyears_department_14"
    assert tags[2] == "employees_without_bonus"


def test_questions_preserve_order(qman):
    """Test that questions are stored in order."""
    expected_tags = [
        "entry_year",
        "entry_year_department_14",
        "hireyears_department_14",
        "employees_without_bonus",
        "employees_with_bonus",
        "total_income_per_employe_department_17",
        "salary_band_per_employee",
        "employees_with_orgunit_name",
        "employees_per_project"
    ]
    actual_tags = [tag for tag, _ in qman.questions]
    assert actual_tags == expected_tags


def test_question_content_multiline(qman):
    """Test that multi-line question content is preserved."""
    _, question = qman[6]  # salary_band_per_employee
    assert "salary band per employee" in question
    assert "low <= 35000" in question
    assert "medium > 35000" in question
    assert "high > 100000" in question
    assert "sorted by salary" in question


def test_invalid_index_type(qman):
    """Test that invalid index type raises TypeError."""
    with pytest.raises(TypeError):
        qman.by_index("invalid")


def test_invalid_getitem_type(qman):
    """Test that invalid __getitem__ type raises TypeError."""
    with pytest.raises(TypeError):
        _ = qman["invalid"]
