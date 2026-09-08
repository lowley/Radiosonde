#!/usr/bin/env python3
"""Read-only HotMovies HLS connectivity probe for a NAS.

Provide an authorized master/variant M3U8 URL and optional HTTP headers via
environment variables. Downloads only playlists and a small range of the first
media segment; never downloads or deletes a full video.

Usage:
  HOTMOVIES_HLS_URL='https://...' HOTMOVIES_COOKIE='...' \
    HOTMOVIES_REFERER='https://www.hotmovies.com/...' python3 tools/hls_session_probe.py

Never paste cookies or signed URLs into issue reports or application logs.
"""
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_PLAYLIST = 2 * 1024 * 1024
SEGMENT_SAMPLE = 4096


def fetch(url, headers, limit):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("Response exceeds diagnostic size limit")
        return response.status, data


def playlist_urls(content, base):
    lines = content.decode("utf-8-sig", errors="replace").splitlines()
    return [urllib.parse.urljoin(base, line.strip()) for line in lines
            if line.strip() and not line.lstrip().startswith("#")]


def same_http_origin(url):
    return urllib.parse.urlsplit(url).scheme in ("http", "https")


def main():
    url = os.environ.get("HOTMOVIES_HLS_URL", "").strip()
    if not same_http_origin(url):
        print("Set HOTMOVIES_HLS_URL to an http(s) playlist URL.")
        return 2
    headers = {"User-Agent": "Mozilla/5.0 (compatible; VidaexoSessionProbe/1.0)"}
    for key, env in (("Cookie", "HOTMOVIES_COOKIE"),
                     ("Referer", "HOTMOVIES_REFERER"),
                     ("Origin", "HOTMOVIES_ORIGIN")):
        if os.environ.get(env):
            headers[key] = os.environ[env]
    try:
        for level in range(3):
            status, content = fetch(url, headers, MAX_PLAYLIST)
            if not content.lstrip().startswith(b"#EXTM3U"):
                print("FAIL: response is not an HLS playlist (possible login page).")
                return 1
            print(f"OK: playlist level {level}, HTTP {status}, {len(content)} bytes")
            urls = playlist_urls(content, url)
            if not urls:
                print("Playlist contains no media URLs.")
                return 1
            next_url = urls[0]
            if not same_http_origin(next_url):
                print("FAIL: non-http(s) resource URL.")
                return 1
            if "#EXT-X-STREAM-INF" in content.decode("utf-8", errors="replace"):
                url = next_url
                continue
            sample_headers = dict(headers)
            sample_headers["Range"] = f"bytes=0-{SEGMENT_SAMPLE - 1}"
            # A server may ignore Range: limit the read regardless.
            try:
                req = urllib.request.Request(next_url, headers=sample_headers)
                with urllib.request.urlopen(req, timeout=25) as response:
                    sample = response.read(SEGMENT_SAMPLE)
                    print(f"OK: first media resource HTTP {response.status}; "
                          f"read {len(sample)} bytes")
                    if not sample:
                        return 1
            except urllib.error.HTTPError as exc:
                print(f"FAIL: first media resource HTTP {exc.code}")
                return 1
            print("PASS: NAS can fetch playlist and media sample with supplied headers.")
            return 0
        print("FAIL: too many nested master playlists.")
        return 1
    except urllib.error.HTTPError as exc:
        print(f"FAIL: HTTP {exc.code} (check authentication, expiry, and headers).")
        return 1
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__} (check network, URL expiry and TLS).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
