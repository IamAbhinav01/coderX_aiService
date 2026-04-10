from app.utils.logger import get_logger
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)


MODEL_NAME = "BAAI/bge-base-en-v1.5"
EXPECTED_DIMS = 768  


_BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(
            f"[Embedder] Loading '{MODEL_NAME}' — "
            "first load downloads ~1.3 GB to HuggingFace cache..."
        )
        _model = SentenceTransformer(MODEL_NAME)
        dims = _model.get_sentence_embedding_dimension()
        if dims != EXPECTED_DIMS:
            raise RuntimeError(
                f"[Embedder] Model produced {dims}-dim vectors but AstraDB "
                f"collection expects {EXPECTED_DIMS}. Recreate the collection "
                "or switch to a model with matching dimensions."
            )
        logger.info(f"[Embedder] Model ready | dims={dims}")
    return _model


def embed_document(text: str) -> list[float]:
   
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    logger.info(f"[Embedder] Document embedded | dims={len(vector)}")
    return vector.tolist()


def embed_query(text: str) -> list[float]:
    model = _get_model()
    vector = model.encode(_BGE_QUERY_PREFIX + text, normalize_embeddings=True)
    logger.info(f"[Embedder] Query embedded | dims={len(vector)}")
    return vector.tolist()
