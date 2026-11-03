"""Physical-transfer bundles for the disconnected domain (Section 12).

Inbound: staging builds a signed bundle -> destination quarantines, verifies
signature + per-file digests, then promotes. Outbound: minimised, signed
report bundle with chain of custody."""
from __future__ import annotations

import json
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .signing import Signer, canonical, sha256_hex

MANIFEST = "BUNDLE_MANIFEST.json"


def build_bundle(src_dir: Path, out_file: Path, signer: Signer, purpose: str, custodian: str) -> Dict:
    src_dir = Path(src_dir)
    files = {str(p.relative_to(src_dir)): sha256_hex(p.read_bytes())
             for p in sorted(src_dir.rglob("*")) if p.is_file() and p.name != MANIFEST}
    meta = {"purpose": purpose, "created_at": datetime.now(timezone.utc).isoformat(),
            "custody": [{"custodian": custodian, "event": "created"}], "files": files}
    meta["signature"] = signer.sign(canonical({k: v for k, v in meta.items() if k != "custody"}))
    meta["key_id"] = signer.key_id
    (src_dir / MANIFEST).write_text(json.dumps(meta, indent=2, sort_keys=True))
    with tarfile.open(out_file, "w:gz") as tar:
        tar.add(src_dir, arcname=".")
    return meta


def quarantine_and_verify(bundle: Path, quarantine_dir: Path, signer: Signer) -> List[str]:
    q = Path(quarantine_dir); q.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle, "r:gz") as tar:
        for m in tar.getmembers():
            if m.name.startswith("/") or ".." in Path(m.name).parts or m.issym() or m.islnk():
                return [f"unsafe path in bundle: {m.name}"]
        tar.extractall(q)
    errs: List[str] = []
    mf = q / MANIFEST
    if not mf.exists():
        return ["bundle manifest missing"]
    meta = json.loads(mf.read_text())
    signed = {k: v for k, v in meta.items() if k not in ("custody", "signature", "key_id")}
    if not signer.verify(canonical(signed), meta.get("signature", "")):
        errs.append("bundle signature invalid")
    present = {str(p.relative_to(q)) for p in q.rglob("*") if p.is_file() and p.name != MANIFEST}
    for rel, digest in meta["files"].items():
        p = q / rel
        if not p.exists():
            errs.append(f"missing file {rel}")
        elif sha256_hex(p.read_bytes()) != digest:
            errs.append(f"digest mismatch {rel}")
    for extra in present - set(meta["files"]):
        errs.append(f"unexpected file {extra}")
    return errs


def promote(quarantine_dir: Path, repo_dir: Path) -> None:
    shutil.copytree(quarantine_dir, repo_dir, dirs_exist_ok=True)
