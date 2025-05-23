import os
import sys

from train_and_register_model import training_pipeline

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_training_pipeline_runs():
    """Test the training pipeline runs without errors."""
    try:
        training_pipeline()
    except Exception as e:
        assert False, f"Training pipeline raised an exception: {e}"
