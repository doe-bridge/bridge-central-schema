"""The generated raised-items page must match raised_items.yaml."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_raised_items_page_is_current():
    """Fails when raised_items.yaml changed without rerunning the renderer."""
    result = subprocess.run(
        [sys.executable, "-m", "ber_central_schema.render_raised_items", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
