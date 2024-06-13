from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from collections import deque
from numpy import ndarray


class Graph:
    def __init__(self, adjacency_map: dict[int, List[int]]) -> None:
        self.adjacency_map = adjacency_map
        self.nodes = list(adjacency_map.keys())

    def __eq__(self, other) -> bool:
        return self.adjacency_map == other

    @property
    def components(self) -> List[List[int]]:
        """Components of the graph (see definition: https://en.wikipedia.org/wiki/Component_(graph_theory))"""
        seen = set()
        components = []

        for root in self.nodes:
            if root not in seen:
                seen.add(root)
                component = []
                queue = deque([root])

                while queue:
                    node = queue.popleft()
                    component.append(node)
                    for neighbour in self.adjacency_map[node]:
                        if neighbour not in seen:
                            seen.add(neighbour)
                            queue.append(neighbour)
                components.append(component)
        return components

    @property
    def multi_node_components(self) -> List[List[int]]:
        """Components with more than one node"""
        multi_node_components = []
        for component in self.components:
            if len(component) > 1:
                multi_node_components.append(component)
        return multi_node_components


class TextComparer:
    def __init__(self, corpus: List[str]) -> None:
        self.corpus = corpus

    @property
    def tfidf_cosine_similarity_matrix(self) -> ndarray:
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(self.corpus)
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        return cosine_sim

    def similarity_graph(self, cutoff=0.45) -> Graph:
        adjacency_map = {}
        for i, row in enumerate(self.tfidf_cosine_similarity_matrix):
            neighbours = []
            for j, similarity_score in enumerate(row):
                if similarity_score > cutoff and i != j:
                    neighbours.append(j)
            adjacency_map[i] = neighbours
        return Graph(adjacency_map)

    def find_groups_of_similar_text(self, cutoff=0.45):
        return self.similarity_graph().multi_node_components
