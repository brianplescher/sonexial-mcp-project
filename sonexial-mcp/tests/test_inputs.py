"""Validation tests for tool input models and their advertised JSON Schemas."""

import pytest
from pydantic import ValidationError

from sonexial_mcp.inputs import TOOL_INPUTS, SearchBooksInput, SearchAuthorsInput


def test_all_nine_tools_registered():
    assert len(TOOL_INPUTS) == 9
    assert "search_books" in TOOL_INPUTS


@pytest.mark.parametrize("spice", [-1, 6])
def test_spice_out_of_range_rejected(spice):
    with pytest.raises(ValidationError):
        SearchBooksInput(spice_min=spice)


def test_spice_range_must_be_ordered():
    with pytest.raises(ValidationError, match="spice_min must be"):
        SearchBooksInput(spice_min=4, spice_max=2)


def test_spice_range_accepts_equal_bounds():
    m = SearchBooksInput(spice_min=3, spice_max=3)
    assert (m.spice_min, m.spice_max) == (3, 3)


def test_unknown_audience_rejected():
    with pytest.raises(ValidationError):
        SearchBooksInput(audience="YA")
    with pytest.raises(ValidationError):
        SearchAuthorsInput(audience="teen")


def test_valid_audience_accepted():
    assert SearchBooksInput(audience="young-adult").audience == "young-adult"


def test_unknown_keys_rejected():
    with pytest.raises(ValidationError):
        SearchBooksInput(spicy_min=2)


def test_advertised_schema_is_strict_and_constrained():
    schema = SearchBooksInput.model_json_schema()
    assert schema["additionalProperties"] is False
    # Optional[int] is advertised as anyOf: the bounded integer branch plus null
    spice_branch = next(b for b in schema["properties"]["spice_min"]["anyOf"] if b.get("type") == "integer")
    assert spice_branch["minimum"] == 0 and spice_branch["maximum"] == 5
    audience = schema["properties"]["audience"]
    # Optional[Literal] is advertised as anyOf with an enum branch
    enums = [b["enum"] for b in audience["anyOf"] if "enum" in b]
    assert enums == [["all-ages", "young-adult", "new-adult", "adult"]]


def test_author_search_accepts_theme_and_audience():
    m = SearchAuthorsInput(themes=["memory"], audience="adult")
    assert m.themes == ["memory"] and m.audience == "adult"
