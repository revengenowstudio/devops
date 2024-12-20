import sys
import os

import pytest
from unittest.mock import patch

sys.path.insert(
    0, os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..')))
