import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from train_and_register_model import training_pipeline

def test_training_pipeline_runs():
    try:
        training_pipeline()
    except Exception as e:
        assert False, f"Training pipeline raised an exception: {e}"
