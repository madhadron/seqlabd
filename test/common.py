import sys; sys.path.append('../')

data_path = 'data'

try:
    import pytest
    slow = pytest.mark.slow
except:
    pass
