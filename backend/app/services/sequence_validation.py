VALID_AA = set("ACDEFGHIKLMNPQRSTVWY")
AMBIGUOUS_AA = set("BXZJUO")

def clean_sequence(sequence: str) -> str:
    return "".join(sequence.upper().split())

def validate_protein_sequence(sequence: str, allow_ambiguous: bool = False) -> str:
    cleaned = clean_sequence(sequence)
    if not cleaned:
        raise ValueError("Protein sequence is empty.")
    allowed = VALID_AA | (AMBIGUOUS_AA if allow_ambiguous else set())
    invalid = sorted(set(cleaned) - allowed)
    if invalid:
        raise ValueError(f"Invalid amino-acid characters found: {invalid}")
    return cleaned
