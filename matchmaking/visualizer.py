from typing import List
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import cv2

class Visualizer:
    
    @staticmethod
    def plot_best_scores(best_scores: List[float], best_scores_iterations: List[float]) -> np.ndarray:
        
        plt.plot(best_scores_iterations, best_scores)
        plt.title("Best Scores")

        plt.draw()
        canvas = plt.gca().figure.canvas  
        canvas.draw() 
        
        image = np.frombuffer(canvas.buffer_rgba(), dtype="uint8")
        image = image.reshape(canvas.get_width_height()[::-1] + (4,))

        plt.close()
        
        return image
    
    @staticmethod
    def write_image(image: np.ndarray, out_dir: str, file_name: str) -> None:
        
        out_dir = Path(out_dir)

        os.makedirs(out_dir, exist_ok=True)
        
        out_path = out_dir / (file_name + ".png")
        
        cv2.imwrite(out_path, image)


