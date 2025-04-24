from abc import abstractmethod

from .types import *

import os
import pathlib
from gensim.models import KeyedVectors
import json

# Disable tqdm progress bars used internally by gensim or other libraries
try:
    import tqdm
    # Override tqdm.tqdm and trange to be no-ops
    tqdm.tqdm = lambda iterable=None, **kwargs: iterable if iterable is not None else []
    tqdm.trange = lambda *args, **kwargs: range(*args)
except ImportError:
    pass

_MODEL = None
model_path = os.environ.get(
    "GLOVE_MODEL_PATH",
    str(pathlib.Path(__file__).resolve().parents[2] / "glove.6B" / "glove.6B.50d.w2v.txt")
)
if os.path.isfile(model_path):
    _MODEL = KeyedVectors.load_word2vec_format(model_path, binary=False)

class Matcher:
    @abstractmethod
    def match(self, request: str, nodes: list[ChatNode], default: str = "") -> ChatNode:
        pass

class StringMatcher(Matcher):
    """
    Simply finds the first choice explicitly mentioned in a request
    """
    def match(self, request: str, nodes: list[ChatNode], default: str = "") -> ChatNode:
        request = request.lower()
        for node in nodes:
            if node.type == "o":
                return node

            keywords = node.content.split(";")
            for word in keywords:
                if word.lower() in request:
                    return node
        return next((node for node in nodes if node.name == default), nodes[0])

    def semantic_match(self, request: str, nodes: list[ChatNode], default: str = "") -> ChatNode:
        """
        Semantic matching using soft cosine similarity with gensim.
        """
        # Initialize semantic log
        if not hasattr(self, 'semantic_log'):
            self.semantic_log = []
            # prepare log directory and semantic log file path
            log_dir = os.environ.get('LOG_DIR', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            self.semantic_log_path = os.environ.get('SEMANTIC_LOG_PATH', os.path.join(log_dir, 'semantic_log.json'))
            # clear existing semantic log
            try:
                with open(self.semantic_log_path, 'w') as f:
                    json.dump([], f, indent=2)
            except Exception as e:
                # Log file write errors but do not affect in-memory log
                import warnings
                warnings.warn(f"Could not clear semantic log file: {e}")

        # Fallback if no model available or no nodes
        if _MODEL is None or not nodes:
            return self.match(request, nodes, default)

        # Exact keyword check: collect all candidates and pick the longest matching keyword
        exact_matches = []
        for node in nodes:
            if node.type == 'o':
                continue
            for kw in node.content.split(';'):
                if kw and kw.lower() in request.lower():
                    exact_matches.append((node, kw))
        if exact_matches:
            # select node with longest keyword match
            matched_node, matched_kw = max(exact_matches, key=lambda x: len(x[1]))
            # log exact match usage
            if not hasattr(self, 'semantic_log'):
                self.semantic_log = []
            self.semantic_log.append((request, matched_node.name, f"exact({matched_kw})"))
            # persist semantic log
            try:
                self._persist_semantic_log()
            except Exception as e:
                import warnings
                warnings.warn(f"Could not persist semantic log: {e}")
            # debug print
            import builtins
            if getattr(builtins, '_CHAT_DEBUG', False):
                print(f"[EXACT] query={request!r} -> {matched_node.name} using keyword {matched_kw!r}")
            return matched_node

        # Prepare and tokenize documents: filter out empty docs
        from re import sub
        def preprocess(doc):
            doc = sub(r'<[^<>]+(>|$)', ' ', doc)
            doc = sub(r'http[s]?://\S+', ' url_token ', doc)
            from gensim.utils import simple_preprocess
            return [token for token in simple_preprocess(doc) if token]
        corpus_docs = []
        candidates = []
        for node in nodes:
            if node.type == 'o':
                continue
            tokens = preprocess(node.content.replace(';', ' '))
            if tokens:
                corpus_docs.append(tokens)
                candidates.append(node)
        if not corpus_docs:
            return self.match(request, nodes, default)

        # Preprocess query
        query = preprocess(request)
        if not query:
            return self.match(request, nodes, default)

        # Build dictionary and TF-IDF
        from gensim.corpora import Dictionary
        from gensim.models import TfidfModel
        dictionary = Dictionary(corpus_docs + [query])
        tfidf = TfidfModel(dictionary=dictionary)
        tfidf_corpus = [tfidf[dictionary.doc2bow(doc)] for doc in corpus_docs]

        # Build similarity matrix, suppress warnings during creation
        from gensim.similarities import SparseTermSimilarityMatrix, WordEmbeddingSimilarityIndex
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            similarity_index = WordEmbeddingSimilarityIndex(_MODEL)
            similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary, tfidf)

        from gensim.similarities import SoftCosineSimilarity
        import warnings
        # Compute soft cosine similarities, suppressing runtime and fortran divide-by-zero warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            index = SoftCosineSimilarity(tfidf_corpus, similarity_matrix)
            query_tf = tfidf[dictionary.doc2bow(query)]
            sims = index[query_tf]

        # Find best matching candidate
        import numpy as np
        try:
            best_idx = int(np.nanargmax(sims))
            best_score = float(sims[best_idx])
        except Exception:
            return self.match(request, nodes, default)
        matched = candidates[best_idx]
        # Log semantic match usage
        self.semantic_log.append((request, matched.name, best_score))
        # persist semantic log
        self._persist_semantic_log()
        # Debug print
        import builtins
        if getattr(builtins, '_CHAT_DEBUG', False):
            print(f"[SEMANTIC] query={request!r} -> {matched.name} (score={best_score:.3f})")
        # Threshold for semantic match
        if best_score >= 0.1:
            return matched
        # Fallback to exact matcher
        return self.match(request, nodes, default)
    
    def _persist_semantic_log(self):
        """Write the accumulated semantic log as JSON to the log file"""
        with open(self.semantic_log_path, 'w') as f:
            json.dump(self.semantic_log, f, indent=2, ensure_ascii=False)