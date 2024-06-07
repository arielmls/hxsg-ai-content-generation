from app.compare_text_similarity import Graph, TextComparer
from numpy import ndarray

def test_Graph_components___empty_adjacency_map():
    graph = Graph(adjacency_map={})
    assert graph.components == []

def test_Graph_components___two_components():
    adjacency_map = {
        0: [1,2],
        1: [0,2],
        2: [0,1],
        3: []
    }
    graph = Graph(adjacency_map)
    assert graph.components == [[0,1,2], [3]]

def test_Graph_multi_node_components___no_multinode_components():
    adjacency_map = {0:[], 1:[]}
    graph = Graph(adjacency_map)
    assert graph.multi_node_components == []

def test_Graph_multi_node_components___has_multinode_component():
    adjacency_map = {
        0: [1,2],
        1: [0,2],
        2: [0,1],
        3: []
    }
    graph = Graph(adjacency_map)
    assert graph.multi_node_components == [[0,1,2]]

def test_TextComparer_tfidf_cosine_similarity_matrix():
    corpus = [
        "this is the first sentence",
        "this is the second sentence"
    ]
    text_comparer = TextComparer(corpus)
    matrix = text_comparer.tfidf_cosine_similarity_matrix
    assert type(matrix) == ndarray
    assert len(matrix) == len(corpus)

def test_TextComparer_similarity_graph():
    corpus = [
        "this is a story all about how my life got flipped turned upside-down",
        "this story is about the way my life got flipped and turned upside-down",
        "would you like some cheese",
        "how old are you"
    ]
    text_comparer = TextComparer(corpus)
    expected_output = Graph({
        0:[1],
        1:[0],
        2:[],
        3:[]
    })
    assert text_comparer.similarity_graph().adjacency_map == expected_output.adjacency_map

def test_TextComparer_find_groups_of_similar_text():
    corpus = [
        "this is a story all about how my life got flipped turned upside-down",
        "this story is about the way my life got flipped and turned upside-down",
        "would you like some cheese",
        "how old are you"
    ]
    text_comparer = TextComparer(corpus)
    assert text_comparer.find_groups_of_similar_text() == [[0,1]]

def test_TextComparer_find_groups_of_similar_text__no_similar_text():
    corpus = [
        "this is a story all about how my life got flipped turned upside-down",
        "how old are you"
    ]
    text_comparer = TextComparer(corpus)
    assert text_comparer.find_groups_of_similar_text() == []
