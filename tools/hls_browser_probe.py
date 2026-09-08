#!/usr/bin/env python3
"""Read-only HotMovies M3U8 discovery using a persistent Chromium profile.

Requires: pip install playwright && python -m playwright install chromium
First run with --headed to sign in interactively. Subsequent runs may be headless.
Do not use a profile simultaneously with another Chromium process.
Never commit the profile or output JSON: both contain access credentials.
"""
import argparse
import asyncio
import json
import os
import re¬
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from playwright.async_api import async_playwright

MOVIE_PATH = re.compile(r"^/\d+/[^/]+\.html$", re.I)

def valid_page(url):
    p = urlparse(url)
    return p.scheme == "https" and p.hostname == "www.hotmovies.com" and bool(MOVIE_PATH.match(p.path))

async def main():
    ap = argparse.ArgumentParser(description="Discover HotMovies HLS URLs without downloading media.")
    ap.add_argument("--page", required=True, help="Full HotMovies scene page URL")
    ap.add_argument("--profile", default="./hotmovies-browser-profile")
    ap.add_argument("--output", default="./hotmovies-hls-result.json")
    ap.add_argument("--headed", action="store_true", help="Show browser for initial interactive login")
    ap.add_argument("--timeout", type=int, default=60, help="Seconds to wait for an HLS request")
    args = ap.parse_args()
    if not valid_page(args.page):
        ap.error("--page must be a HotMovies HTTPS scene URL (/123/name.html)")
    if args.timeout < 5 or args.timeout > 600:
        ap.error("--timeout must be between 5 and 600 seconds")
    profile = Path(args.profile).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if output.is_relative_to(profile):
        ap.error("--output must be outside the browser profile directory")
    profile.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(profile, 0o700)
    except OSError:
        pass
    candidates = []
    seen = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile), headless=not args.headed,
            accept_downloads=False,
        )
        def record(request):
            url = request.url
            path = urlparse(url).path.lower()
            if ".m3u8" not in path or url in seen:
                return
            seen.add(url)
            params = parse_qs(urlparse(url).query)
            candidates.append({
                "url": url,
                "observed_at": int(time.time()),
                "expires_at": int(params["e"][0]) if params.get("e", [""])[0].isdigit() else None,
                "resource_type": request.resource_type,
            })
            print(f"HLS detected ({len(candidates)}); URL withheld from console")
        browser.on("request", record)
        page = browser.pages[0] if browser.pages else await browser.new_page()
        try:
            await page.goto(args.page, wait_until="domcontentloaded", timeout=30000)
            # CatCatch injects this invisible iframe into the scene page.
            player_url = args.page.split("?")[0] + "?viewpart=videoplayer"
            await page.evaluate("""url => {
                if (!document.getElementById('vidaexo-hls-probe-player')) {
                    const f = document.createElement('iframe');
                    f.id = 'vidaexo-hls-probe-player';
                    f.src = url;
                    f.style.cssText = 'position:fixed;width:1px;height:1px;left:-10000px;top:-10000px;opacity:0;pointer-events:none';
                    document.documentElement.appendChild(f);
                }
            }""", player_url)
            end = time.monotonic() + args.timeout
            while time.monotonic() < end and not candidates:
                await asyncio.sleep(0.5)
            if args.headed and not candidates:
                print("No HLS request yet. If login is needed, complete it in the browser.")
                end = time.monotonic() + args.timeout
                while time.monotonic() < end and not candidates:
                    await asyncio.sleep(0.5)
        finally:
            await browser.close()
    if not candidates:
        print("FAIL: no HLS request observed. Check login, page, and player behavior.")
        return 1
    payload = {"page": args.page, "captured_at": int(time.time()), "candidates": candidates}
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".hls-", dir=str(output.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(temp_name, output)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(f"PASS: {len(candidates)} HLS URL(s) captured; sensitive results stored in {output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
