import pytest
from app.services.sequence_validation import validate_protein_sequence

def test_valid_sequence():
    assert validate_protein_sequence("ACD EFG") == "ACDEFG"

def test_invalid_sequence():
    with pytest.raises(ValueError):
        validate_protein_sequence("ACD123")

def test_ambiguous_allowed():
    assert validate_protein_sequence("ACDX", allow_ambiguous=True) == "ACDX"
