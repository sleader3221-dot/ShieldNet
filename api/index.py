import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
sys.path.insert(0, backend_dir)

from mangum import Mangum
from main import app

handler = Mangum(app)
