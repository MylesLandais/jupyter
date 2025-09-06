#!/usr/bin/env python3
import argparse, json, os, sys, time
from pathlib import Path
from typing import Dict, Any, Iterable, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5, connect=5, read=5, backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"])
    )
    s.headers.update({"User-Agent": "bulk-img-dl/1.0"})
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s

def load_manifest(src: str) -> Dict[str, Any]:
    if src.startswith("http://") or src.startswith("https://"):
        with make_session().get(src, timeout=30) as r:
            r.raise_for_status()
            return r.json()
    else:
        with open(src, "r", encoding="utf-8") as f:
            return json.load(f)

def iter_images(manifest: Dict[str, Any]) -> Iterable[Tuple[str, str]]:
    """Yield (id, href) for every image in every category."""
    for cat in manifest.get("categories", []):
        for img in cat.get("images", []):
            img_id = img.get("id")            # e.g. artwork/010-Body/blue_gopher.png
            href   = img.get("href")          # full https URL to the PNG
            if img_id and href:
                yield img_id, href

def download_one(session: requests.Session, out_root: Path, img_id: str, url: str, overwrite: bool=False) -> str:
    out_path = out_root / img_id
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not overwrite:
        return f"SKIP  {img_id}"
    with session.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        tmp = out_path.with_suffix(out_path.suffix + ".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 15):
                if chunk:
                    f.write(chunk)
        os.replace(tmp, out_path)
    return f"OK    {img_id}"

def main():
    ap = argparse.ArgumentParser(description="Download images listed in a gopherize-me JSON manifest.")
    ap.add_argument("--json", required=True, help="Path or URL to the JSON manifest")
    ap.add_argument("--out", default="downloads", help="Output folder root (default: downloads)")
    ap.add_argument("--workers", type=int, default=8, help="Parallel downloads (default: 8)")
    ap.add_argument("--overwrite", action="store_true", help="Re-download even if the file exists")
    args = ap.parse_args()

    manifest = load_manifest(args.json)
    items = list(iter_images(manifest))
    if not items:
        print("No images found in manifest.", file=sys.stderr)
        sys.exit(1)

    out_root = Path(args.out)
    sess = make_session()

    print(f"Found {len(items)} images. Downloading to: {out_root.resolve()}")
    start = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(download_one, sess, out_root, img_id, url, args.overwrite) for img_id, url in items]
        for fut in as_completed(futs):
            try:
                msg = fut.result()
                results.append(msg)
                print(msg)
            except Exception as e:
                print(f"FAIL  {e}", file=sys.stderr)

    elapsed = time.time() - start
    ok = sum(1 for r in results if r.startswith("OK"))
    skip = sum(1 for r in results if r.startswith("SKIP"))
    print(f"\nDone in {elapsed:.1f}s — OK: {ok}, Skipped: {skip}, Total: {len(items)}")

if __name__ == "__main__":
    main()
