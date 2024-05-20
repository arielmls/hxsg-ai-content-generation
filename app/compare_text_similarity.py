from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple


class TextComparer:
    def __init__(self, corpus) -> None:
        self.corpus = corpus

    @property
    def tfidf_cosine_similarity_matrix(self):
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(self.corpus)
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        return cosine_sim

    def make_similar_groups_from_pairs(self, pairs: List[Tuple[int]]):
        groups = []
        for pair in pairs:
            added_to_group = False
            for group in groups:
                if pair[0] in group or pair[1] in group:
                    group.append(pair[0])
                    group.append(pair[1])
                    added_to_group = True

            if not added_to_group:
                groups.append([pair[0], pair[1]])

        for i, group in enumerate(groups):
            groups[i] = list(dict.fromkeys(group))

        return groups

    def find_similar_pairs(self, cutoff=0.55):
        similarity_matrix = self.tfidf_cosine_similarity_matrix
        similar_pairs = []
        for i, row in enumerate(similarity_matrix):
            for j, similarity_score in enumerate(row):
                if j < i and similarity_score > cutoff:
                    similar_pairs.append((i, j))
                    print(f"pair:{(i,j)}, scrore: {similarity_score}")
        return similar_pairs

    def find_similar_groups(self, cutoff=0.55):
        return self.make_similar_groups_from_pairs(self.find_similar_pairs(cutoff))
