from playwright.sync_api import sync_playwright
from pathlib import Path
import functools
import http.server
import json
import os
import socketserver
import threading
import time

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT_DIR = Path(os.environ.get("KIOKU_QA_OUT", "/tmp/kioku-round35-qa-media"))
OUT_DIR.mkdir(parents=True, exist_ok=True)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def start_server():
    handler = functools.partial(QuietHandler, directory=str(DIST))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, f"http://127.0.0.1:{port}"


def main():
    httpd, base_url = start_server()
    summary = {"baseUrl": base_url, "widths": {}, "webgl": {}, "fallbacks": {}}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--enable-webgl", "--ignore-gpu-blocklist", "--use-angle=metal"],
            )

            # 1. Full interactive WebGL & Dual-Realm verification at 1440x900 (with video)
            v_ctx = browser.new_context(
                viewport={"width": 1440, "height": 900},
                device_scale_factor=1,
                record_video_dir=str(OUT_DIR),
                record_video_size={"width": 1280, "height": 720},
            )
            page = v_ctx.new_page()
            errors, bad_responses = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("response", lambda r: bad_responses.append((r.status, r.url)) if r.status >= 400 else None)

            t0 = time.perf_counter()
            page.goto(f"{base_url}/index.html", wait_until="networkidle", timeout=30000)
            page.wait_for_function(
                "() => window.__KIOKU_DRAGON_DIAG__ && window.__KIOKU_DRAGON_DIAG__.mode === 'webgl-round35'",
                timeout=20000,
            )
            load_ms = round((time.perf_counter() - t0) * 1000, 1)
            page.wait_for_timeout(500)

            diag_init = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__")
            assert diag_init["boneCount"] >= 70, f"Expected >=70 deform bones: {diag_init}"
            assert diag_init["meshCount"] >= 12, f"Expected >=12 meshes: {diag_init}"
            for clip in ["SwimLoop", "SurfaceCrossing", "WaterToCoralTransform", "CoralFlightLoop", "CoralToWaterDescent"]:
                assert clip in diag_init["clips"], f"Missing clip {clip}"

            # Water Realm check & screenshot
            page.click('[data-realm-select="water"]')
            page.wait_for_timeout(950)
            diag_water = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__")
            assert diag_water["realmBlend"] < 0.08, f"Water realmBlend too high: {diag_water}"
            water_shot = OUT_DIR / "desktop_1440_water.png"
            page.screenshot(path=str(water_shot))

            # Coral Flight transition check (verify intermediate continuous blend, then settled Coral)
            page.click('[data-realm-select="coral"]')
            page.wait_for_timeout(220)
            diag_mid = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__")
            assert 0.02 < diag_mid["realmBlend"] < 0.96, f"Realm blend snapped instead of interpolating: {diag_mid}"
            page.wait_for_timeout(1250)
            diag_coral = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__")
            assert diag_coral["realmBlend"] > 0.92, f"Coral realmBlend did not settle: {diag_coral}"
            assert diag_coral["activeClip"] == "CoralFlightLoop"
            coral_shot = OUT_DIR / "desktop_1440_coral.png"
            page.screenshot(path=str(coral_shot))

            # Prove skeletal deformation over time with stationary camera
            shot_a = page.locator("#kioku-dragon-canvas").screenshot()
            page.wait_for_timeout(380)
            shot_b = page.locator("#kioku-dragon-canvas").screenshot()
            assert shot_a != shot_b, "Canvas pixels identical across 380ms — animation did not deform!"

            # Orbit drag + Reset camera + Keyboard orbit
            yaw_before = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__.orbitYaw")
            box = page.locator("#kioku-dragon-canvas").bounding_box()
            cx, cy = box["x"] + box["width"] * 0.5, box["y"] + box["height"] * 0.5
            page.mouse.move(cx, cy)
            page.mouse.down()
            page.mouse.move(cx + 180, cy - 40, steps=8)
            page.mouse.up()
            page.wait_for_timeout(350)
            yaw_dragged = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__.orbitYaw")
            assert abs(yaw_dragged - yaw_before) > 0.12, f"Pointer drag did not orbit: {yaw_before} -> {yaw_dragged}"

            page.click("[data-dragon-reset]")
            page.wait_for_timeout(650)
            yaw_reset = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__.orbitYaw")
            assert abs(yaw_reset - yaw_before) < 0.08, f"Reset view did not restore yaw: {yaw_reset} vs {yaw_before}"

            page.focus("#kioku-dragon-canvas")
            page.keyboard.press("ArrowLeft")
            page.wait_for_timeout(300)
            yaw_key = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__.orbitYaw")
            assert yaw_key > yaw_reset + 0.03, "Keyboard ArrowLeft orbit failed"

            # Pause / Play precedence
            page.click("[data-dragon-motion-toggle]")
            page.wait_for_timeout(120)
            diag_paused = page.evaluate("() => window.__KIOKU_DRAGON_DIAG__")
            assert diag_paused["paused"] is True
            assert page.get_attribute("[data-dragon-scene]", "data-dragon-state") == "paused"
            page.click("[data-dragon-motion-toggle]")
            page.wait_for_timeout(200)
            assert page.evaluate("() => window.__KIOKU_DRAGON_DIAG__.paused") is False

            assert not errors, f"Console/page errors: {errors}"
            assert not bad_responses, f"HTTP errors: {bad_responses}"

            summary["webgl"] = {
                "loadMs": load_ms,
                "diagWater": diag_water,
                "diagMid": diag_mid,
                "diagCoral": diag_coral,
                "orbitVerified": True,
                "pausePlayVerified": True,
                "skeletalMotionVerified": True,
            }
            v_ctx.close()

            # 2. Responsive widths check (320, 375, 390, 768, 1440) + mobile 390x844 CTA guardrail
            for w in [320, 375, 390, 768, 1440]:
                h = 844 if w <= 390 else 900
                ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
                pg = ctx.new_page()
                pg_errs = []
                pg.on("pageerror", lambda e, lst=pg_errs: lst.append(str(e)))
                pg.goto(f"{base_url}/index.html", wait_until="networkidle", timeout=30000)
                pg.wait_for_function("() => Boolean(window.__KIOKU_DRAGON_DIAG__)", timeout=15000)
                pg.wait_for_timeout(450)
                ov = pg.evaluate("() => ({doc: document.documentElement.scrollWidth, vp: window.innerWidth})")
                assert ov["doc"] <= ov["vp"] + 2, f"Overflow at {w}: {ov}"
                cta_box = None
                if w == 390:
                    cta_box = pg.locator('.hero-mobile-entry a[href="./collection.html"]').bounding_box()
                    assert cta_box and cta_box["y"] + cta_box["height"] <= 844, f"Mobile CTA pushed below fold: {cta_box}"
                pg.screenshot(path=str(OUT_DIR / f"responsive_{w}x{h}.png"))
                assert not pg_errs, f"Errors at {w}: {pg_errs}"
                summary["widths"][str(w)] = {"overflow": ov, "mobileCtaBottom": round(cta_box["y"] + cta_box["height"], 1) if cta_box else None}
                ctx.close()

            # 3. Reduced-motion & WebGL-disabled fallbacks
            rm_ctx = browser.new_context(viewport={"width": 1280, "height": 800}, reduced_motion="reduce")
            rm_pg = rm_ctx.new_page()
            rm_pg.goto(f"{base_url}/index.html", wait_until="networkidle")
            assert rm_pg.get_attribute("[data-dragon-scene]", "data-dragon-state") == "fallback"
            assert rm_pg.get_attribute("[data-dragon-scene]", "data-fallback-reason") == "reduced-motion"
            fb_nw = rm_pg.evaluate("() => document.querySelector('[data-dragon-fallback-img]').naturalWidth")
            assert fb_nw > 400, f"Fallback image not loaded: {fb_nw}"
            rm_pg.screenshot(path=str(OUT_DIR / "fallback_reduced_motion.png"))
            rm_ctx.close()

            ng_ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            ng_pg = ng_ctx.new_page()
            ng_pg.add_init_script("window.__KIOKU_DISABLE_WEBGL__ = true;")
            ng_pg.goto(f"{base_url}/index.html", wait_until="networkidle")
            assert ng_pg.get_attribute("[data-dragon-scene]", "data-dragon-state") == "fallback"
            summary["fallbacks"] = {"reducedMotion": True, "webglUnavailable": True, "fallbackImageWidth": fb_nw}
            ng_ctx.close()

            browser.close()
    finally:
        httpd.shutdown()

    (OUT_DIR / "qa_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
