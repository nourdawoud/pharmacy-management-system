"""Run the working Phase 1 Flask application.

The current functional demo lives in the repository-root app.py. Load it by
file path because the separate app/ package is a modular refactor scaffold and
would otherwise shadow app.py during Python imports.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_APP_FILE = Path(__file__).resolve().with_name("app.py")
_spec = spec_from_file_location("pharmacy_root_app", _APP_FILE)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Could not load application from {_APP_FILE}")
_pharmacy = module_from_spec(_spec)
_spec.loader.exec_module(_pharmacy)

app = _pharmacy.app

if __name__ == "__main__":
    app.run(debug=True)
