import sys
import os
from unittest.mock import patch

import pytest


# sys.path.insert(
#     0, os.path.abspath(
#         os.path.join(
#             os.path.dirname(__file__), '..')))

sys.path.insert(
    0, os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '../src/')))
