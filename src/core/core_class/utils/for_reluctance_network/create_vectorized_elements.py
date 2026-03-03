from src.core.core_class.models.VectorizedElements import VectorizedElements

def init_vectorized_elements(reluctance_network):
    if reluctance_network.vectorized_optimization is True:
        return VectorizedElements(reluctance_network= reluctance_network)

    else:
        return None