import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def interpret_similarity(score: float) -> str:
    if score >= 0.85:
        return "Very high embedding similarity. Investigate shared function, family, or conserved domains."
    if score >= 0.65:
        return "Moderate-to-high similarity. Could indicate related biological properties."
    if score >= 0.35:
        return "Weak-to-moderate similarity. Interpret cautiously and compare annotations."
    return "Low similarity. These proteins may be functionally or evolutionarily distant."
