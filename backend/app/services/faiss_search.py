import numpy as np


def search_faiss(
    query_vector: np.ndarray,
    candidates: list[dict],
    top_k: int,
) -> list[tuple[dict, float]]:
    matrix = np.ascontiguousarray(
        np.vstack([item["vector"] for item in candidates]).astype(np.float32)
    )
    query = np.ascontiguousarray(query_vector.reshape(1, -1).astype(np.float32))

    try:
        import faiss
    except ImportError:
        matrix_norm = np.linalg.norm(matrix, axis=1, keepdims=True)
        query_norm = np.linalg.norm(query, axis=1, keepdims=True)
        matrix = matrix / np.where(matrix_norm == 0, 1, matrix_norm)
        query = query / np.where(query_norm == 0, 1, query_norm)
        scores = matrix @ query.T
        ranked = np.argsort(scores[:, 0])[::-1][:top_k]
        return [(candidates[int(index)], float(scores[int(index), 0])) for index in ranked]

    faiss.normalize_L2(matrix)
    faiss.normalize_L2(query)

    if len(candidates) < 32:
        index = faiss.IndexFlatIP(matrix.shape[1])
    else:
        index = faiss.IndexHNSWFlat(matrix.shape[1], 32, faiss.METRIC_INNER_PRODUCT)
        index.hnsw.efSearch = max(32, top_k * 2)

    index.add(matrix)

    scores, indices = index.search(query, min(top_k, len(candidates)))

    return [
        (candidates[int(index)], float(score))
        for index, score in zip(indices[0], scores[0], strict=False)
        if index >= 0
    ]
