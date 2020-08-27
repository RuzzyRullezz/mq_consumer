import sys
from pathlib import Path


def setup():
    env_dir = str(Path(__file__).resolve(strict=True).parent.parent)
    sys.path.append(str(env_dir))
