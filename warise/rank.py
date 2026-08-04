import math
import re
from collections import Counter

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "how",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "will",
    "with",
    "you",
    "your",
}


def tokenize(text, remove_stop=True):
    tokens = re.findall(r"\w+", text.lower())

    if remove_stop:
        tokens = [token for token in tokens if token not in STOPWORDS]

    return [token for token in tokens if len(token) > 1]


class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.doc_count = len(corpus)
        self.doc_len = [len(doc) for doc in corpus]
        self.avgdl = sum(self.doc_len) / self.doc_count if self.doc_count else 0.0

        self.tf = []
        self.df = Counter()

        for doc in corpus:
            counts = Counter(doc)
            self.tf.append(counts)

            for term in set(doc):
                self.df[term] += 1

        self.idf = {
            term: math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1.0)
            for term, df in self.df.items()
        }

    def score(self, query):
        scores = []

        for i, counts in enumerate(self.tf):
            score = 0.0
            dl = self.doc_len[i] or 1

            for term in query:
                if term not in counts:
                    continue

                tf = counts[term]
                idf = self.idf.get(term, 0.0)
                denominator = tf + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1.0))
                score += idf * tf * (self.k1 + 1) / (denominator or 1.0)

            scores.append(score)

        return scores


def rank_chunks(chunks, query, top_k=12):
    if not chunks:
        return []

    query_tokens = tokenize(query)

    if not query_tokens:
        query_tokens = tokenize(query, remove_stop=False)

    if not query_tokens:
        return [{**chunk, "score": 0.0} for chunk in chunks[:top_k]]

    corpus = [tokenize(chunk.get("text", "")) for chunk in chunks]
    bm25 = BM25(corpus)
    scores = bm25.score(query_tokens)

    ranked = []
    query_token_set = set(query_tokens)

    for chunk, score in zip(chunks, scores):
        title_tokens = set(tokenize(chunk.get("title", "")))
        bonus = 0.2 * len(title_tokens.intersection(query_token_set))

        if query.lower() in chunk.get("text", "").lower():
            bonus += 1.0

        ranked.append({**chunk, "score": round(score + bonus, 4)})

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]