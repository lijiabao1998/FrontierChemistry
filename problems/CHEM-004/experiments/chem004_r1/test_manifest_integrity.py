"""Maintenance tests for the hash gate, with corrupted bytes and malformed inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from verify_manifest import verify


class ManifestTests(unittest.TestCase):
    def test_incompatible_bundle_blocks_before_import_without_writing_result(self):
        here = Path(__file__).resolve().parent
        result = here.parent.parent / "results/r1/chem004_r1_results.json"
        before = result.read_bytes()
        code = "import sysconfig; sysconfig.get_platform=lambda: 'linux-x86_64'; import freesolv_validator as fv; raise SystemExit(fv.main())"
        process = subprocess.run([sys.executable, "-B", "-c", code], cwd=here,
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 2, process.stderr)
        self.assertIn('BLOCKED_DEPENDENCY', process.stdout)
        self.assertNotIn('Traceback', process.stderr)
        self.assertEqual(result.read_bytes(), before)

    def test_incompatible_runner_blocks_before_chemical_assertions(self):
        here = Path(__file__).resolve().parent
        result = here.parent.parent / "results/r1/chem004_r1_results.json"
        before = result.read_bytes()
        code = "import sysconfig,runpy; sysconfig.get_platform=lambda: 'linux-x86_64'; runpy.run_path('tests_regression.py', run_name='__main__')"
        process = subprocess.run([sys.executable, "-B", "-c", code], cwd=here,
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 2, process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["verdict"], "BLOCKED_DEPENDENCY")
        self.assertEqual(payload["tests_run"], 0)
        self.assertIs(payload["result_written"], False)
        self.assertNotIn('Traceback', process.stderr)
        self.assertEqual(result.read_bytes(), before)

    def test_exact_bytes_pass(self):
        body = b"one\ntwo\n"
        files = {"data.txt": body, "results/r1/hashes.txt":
                 (hashlib.sha256(body).hexdigest() + " *data.txt\n").encode()}
        self.assertEqual(verify(files.__getitem__), (1, []))

    def test_line_ending_change_is_not_normalised_away(self):
        body = b"one\ntwo\n"
        files = {"data.txt": body.replace(b"\n", b"\r\n"), "results/r1/hashes.txt":
                 (hashlib.sha256(body).hexdigest() + " *data.txt\n").encode()}
        self.assertTrue(verify(files.__getitem__)[1])

    def test_empty_malformed_duplicate_and_traversal_fail(self):
        digest = hashlib.sha256(b"data").hexdigest()
        for manifest in ["", "not-a-hash *data.txt", digest + " *../data.txt",
                         f"{digest} *data.txt\n{digest} *data.txt\n"]:
            files = {"data.txt": b"data", "results/r1/hashes.txt": manifest.encode()}
            self.assertTrue(verify(files.__getitem__)[1], manifest)

    def test_missing_file_fails(self):
        def missing(name):
            if name == "results/r1/hashes.txt":
                return ("0" * 64 + " *missing.txt\n").encode()
            raise FileNotFoundError(name)
        self.assertTrue(verify(missing)[1])


if __name__ == "__main__":
    unittest.main()
