"""
Environment Verification Test Suite
"""

def test_environment_imports():
    """Verify that all core dependencies are installed and importable."""
    # pyrefly: ignore [missing-import]
    import streamlit
    import pandas
    # pyrefly: ignore [missing-import]
    import numpy
    import sklearn
    # pyrefly: ignore [missing-import]
    import plotly
    import networkx
    # pyrefly: ignore [missing-import]
    import dotenv
    import requests

    assert streamlit.__version__ is not None
    assert pandas.__version__ is not None
    assert numpy.__version__ is not None
    assert sklearn.__version__ is not None
    assert plotly.__version__ is not None
    assert networkx.__version__ is not None
    assert dotenv.__file__ is not None
    assert requests.__version__ is not None
    print("All environment imports succeeded successfully!")

if __name__ == "__main__":
    test_environment_imports()
