import os
import pathlib
import re
import warnings
from abc import ABC, abstractmethod
from typing import List, Optional

import numpy as np
from gensim.models import KeyedVectors, TfidfModel
from gensim.utils import simple_preprocess
from gensim.corpora import Dictionary
from gensim.similarities import SparseTermSimilarityMatrix, WordEmbeddingSimilarityIndex, SoftCosineSimilarity

from .types import ChatNode
from .debug_mode import init_semantic_log, log_semantic

_MODEL: Optional[KeyedVectors] = None
_MODEL_PATH: Optional[str] = None
MODEL_PATH_ENV = "GLOVE_MODEL_PATH"

# suppress divide-by-zero warnings from gensim term similarity
warnings.filterwarnings(
    'ignore',
    category=RuntimeWarning,
    module='gensim.similarities.termsim'
)

def _get_model() -> Optional[KeyedVectors]:
    """Lazily load or reload the GloVe model from env if changed."""
    global _MODEL, _MODEL_PATH
    path = os.environ.get(MODEL_PATH_ENV)
    if not path:
        return None
    if path != _MODEL_PATH:
        if os.path.isfile(path):
            _MODEL = KeyedVectors.load_word2vec_format(path, binary=False)
            _MODEL_PATH = path
        else:
            _MODEL = None
            _MODEL_PATH = None
    return _MODEL


def _preprocess(text: str) -> List[str]:
    """Tokenize and clean text."""
    text = re.sub(r'<[^<>]+>', ' ', text)
    text = re.sub(r'http[s]?://\S+', ' url ', text)
    return [t for t in simple_preprocess(text) if t]


class Matcher(ABC):
    @abstractmethod
    def match(self, request: str, nodes: List[ChatNode], default: str = "") -> ChatNode:
        pass


class StringMatcher(Matcher):
    """Literal and semantic matcher for ChatNodes."""
    def __init__(self):
        # clear semantic log storage
        init_semantic_log()

    def match(self, request: str, nodes: List[ChatNode], default: str = "") -> ChatNode:
        req = request.lower()
        # type 'o' always wins
        for n in nodes:
            if n.type == 'o':
                return n
        # keyword match
        for n in nodes:
            if any(kw and kw.lower() in req for kw in n.content.split(';')):
                return n
        return next((n for n in nodes if n.name == default), nodes[0])

    def semantic_match(self, request: str, nodes: List[ChatNode], default: str = "") -> ChatNode:
        # 1) Exact keyword matching: pick the node with the longest matching keyword
        req = request.lower()
        exact = [ (n, kw)
                  for n in nodes if n.type != 'o'
                  for kw in n.content.split(';')
                  if kw and kw.lower() in req ]
        if exact:
            # choose the most specific keyword and log it
            n, kw = max(exact, key=lambda x: len(x[1]))
            self._log(request, n.name, f"exact({kw})")
            return n
        # 2) Load or reload the GloVe embedding model if needed
        model = _get_model()
        # fallback to simple match if model missing or no candidates
        if not model or not nodes:
            return self.match(request, nodes, default)
        # 3) Prepare tokenized documents for Soft Cosine
        corpus = [_preprocess(n.content.replace(';', ' ')) for n in nodes if n.type != 'o']
        tokens = _preprocess(request)
        # if preprocessing yields no tokens, fallback
        if not corpus or not tokens:
            return self.match(request, nodes, default)
        # 4) Build dictionary and TF-IDF representation
        dict_ = Dictionary(corpus + [tokens])
        tfidf = TfidfModel(dictionary=dict_)
        tfidf_corpus = [tfidf[dict_.doc2bow(c)] for c in corpus]
        # remove docs that produce empty TF-IDF (zero vectors)
        cand_nodes = [n for n in nodes if n.type != 'o']
        valid_idxs = [i for i, doc in enumerate(tfidf_corpus) if doc]
        if not valid_idxs:
            return self.match(request, nodes, default)
        filtered_corpus = [tfidf_corpus[i] for i in valid_idxs]
        # 5) Create a SoftCosineSimilarity index using word embeddings, suppress NumPy runtime warnings
        with np.errstate(divide='ignore', invalid='ignore'):
            sim_index = WordEmbeddingSimilarityIndex(model)
            matrix = SparseTermSimilarityMatrix(sim_index, dict_, tfidf)
            softcos = SoftCosineSimilarity(filtered_corpus, matrix)
        # 6) Transform query and compute similarity scores
        vec = tfidf[dict_.doc2bow(tokens)]
        # compute similarity scores, suppress divide-by-zero/runtime warnings
        with np.errstate(divide='ignore', invalid='ignore'):
            scores_raw = softcos[vec]
        # map back to original candidates, zero for removed docs
        scores = np.zeros(len(cand_nodes))
        for idx_filt, orig_i in enumerate(valid_idxs):
            scores[orig_i] = float(scores_raw[idx_filt])
        # 7) Pick the highest-scoring candidate (or fallback)
        idx = int(np.nanargmax(scores)) if scores.size else -1
        if idx < 0:
            return self.match(request, nodes, default)
        # 8) Determine best candidate and enforce minimum similarity threshold
        best = [n for n in nodes if n.type != 'o'][idx]
        score = float(scores[idx])
        # low confidence: log and signal reprompt
        if score < 0.1:
            self._log(request, best.name, f"low_confidence({score})")
            return None
        # high confidence: log and return choice
        self._log(request, best.name, score)
        return best

    def _log(self, req: str, name: str, info):
        # delegate to debug_mode
        log_semantic(req, name, info)