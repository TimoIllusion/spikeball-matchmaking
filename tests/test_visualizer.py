from matchmaking.visualizer import Visualizer


def test_visualizer_plot():
    
    img = Visualizer.plot_best_scores([3, 2, 1], [10, 20, 30])
    
    assert img.any(), "Image is empty"