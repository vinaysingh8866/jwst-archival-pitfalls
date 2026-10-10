import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import checklist  # noqa: E402

REQUIRED = {"id", "domain", "signature", "cause", "check"}


def test_every_entry_is_complete_and_unique():
    items = checklist.load()
    assert len(items) >= 30
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids))
    for i in items:
        missing = REQUIRED - set(i)
        assert not missing, f"{i.get('id')} missing {missing}"


def test_readme_mentions_every_domain():
    readme = (HERE / "README.md").read_text().lower()
    for d in {i["domain"] for i in checklist.load()}:
        assert d.split("-")[0] in readme, d


def test_cli_json_and_domain_filter():
    out = subprocess.run([sys.executable, str(HERE / "checklist.py"), "--json", "--domain", "archive-access"],
                         capture_output=True, text=True, check=True).stdout
    items = json.loads(out)
    assert items and all(i["domain"] == "archive-access" for i in items)
    assert subprocess.run([sys.executable, str(HERE / "checklist.py"), "--domain", "nope"]).returncode == 2
