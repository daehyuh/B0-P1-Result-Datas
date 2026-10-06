"""Small reproducible check of the relation-index data contract."""

from __future__ import annotations

import shutil
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from relation_index.config import Settings
from relation_index.indexer import build_index
from relation_index.queries import Queries
from relation_index.snapshot import collect
from relation_index.storage import Store


class RelationIndexTest(unittest.TestCase):
    def test_source_package_names_are_not_treated_as_build_outputs(self) -> None:
        for package_name in ("build", "target", "vendor"):
            with self.subTest(package_name=package_name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                project = root / "source"
                package = project / "src" / "main" / "java" / "demo" / package_name
                package.mkdir(parents=True)
                (package / "Kept.java").write_text("class Kept {}\n", encoding="utf-8")
                generated = project / package_name
                generated.mkdir()
                (generated / "Skipped.java").write_text("class Skipped {}\n", encoding="utf-8")
                (project / ".gitignore").write_text(f"{package_name}/\n", encoding="utf-8")
                store = Store(Settings(root / "data"))

                manifest = collect(project, store)
                paths = {item["path"] for item in manifest["files"]}

                self.assertIn(f"src/main/java/demo/{package_name}/Kept.java", paths)
                self.assertNotIn(f"{package_name}/Skipped.java", paths)

    def test_java_call_and_role_facts(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "source"
            shutil.copytree(ROOT / "tests" / "fixture", project)
            store = Store(Settings(root / "data"))
            project_id = uuid.uuid4().hex
            with store.connect() as db:
                db.execute(
                    "INSERT INTO projects(id,name,root,created_at) VALUES(?,?,?,?)",
                    (project_id, "fixture", str(project), time.time()),
                )
            job = store.enqueue(project_id, "index", {})
            store.execute("UPDATE jobs SET status='running' WHERE id=?", (job["id"],))
            result = build_index(store, job)
            metrics = result["metrics"]
            self.assertEqual(metrics["files"], 2)
            self.assertEqual(metrics["calls"], 1)
            self.assertEqual(metrics["parse_errors"], [])
            query = Queries(store, result["snapshot_id"])
            symbol = query.symbols("Service.find")["items"][0]
            context = query.context(symbol["id"])
            self.assertTrue(any(row["kind"] == "CALLS" for row in context["relations"]["items"]))
            facts = query.facts()["items"]
            self.assertEqual({row["kind"] for row in facts}, {"route", "input"})


if __name__ == "__main__":
    unittest.main()
