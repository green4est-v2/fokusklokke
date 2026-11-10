# Fokusklokke lamp for the Pimoroni Galactic Unicorn (Pico 2 W, MicroPython).
# index.html sends one JSON line over USB on every state change:
#   {"p": "focus" | "break" | "paused" | "idle", "left": seconds, "free": "H:MM"}
# The lamp counts down on its own, so it falls back to "LEDIG" if the browser goes away.
import json

COLOURS = {
    "focus": (232, 85, 59),
    "break": (255, 194, 60),
    "paused": (255, 194, 60),
    "idle": (31, 175, 148),
}
LABELS = {"focus": "FOKUS", "break": "PAUSE", "paused": "VENT", "idle": "LEDIG"}
SIGNS = {"C": ("Kaffepaus", (160, 82, 30)), "D": ("Lunsj!", (255, 255, 255))}
SPEED = 20  # ticker speed, pixels per second
GAP = 16  # blank pixels between the end of the ticker text and its next start
MAX_LEFT = 4 * 3600
MAX_LINE = 200


def valid_clock(s):
    parts = s.split(":")
    return (len(parts) == 2 and 1 <= len(parts[0]) <= 2 and len(parts[1]) == 2
            and parts[0].isdigit() and parts[1].isdigit()
            and int(parts[0]) < 24 and int(parts[1]) < 60)


def parse(line):
    """Return (state, left_seconds, free) for a valid message, else None."""
    if len(line) > MAX_LINE:
        return None
    try:
        m = json.loads(line)
    except ValueError:
        return None
    if not isinstance(m, dict) or m.get("p") not in COLOURS:
        return None
    if m["p"] == "idle":
        return ("idle", 0, "")
    left, free = m.get("left"), m.get("free", "")
    if type(left) is not int or not 0 <= left <= MAX_LEFT:
        return None
    if not isinstance(free, str) or (free and not valid_clock(free)):
        return None
    return (m["p"], left, free)


def texts(state, left_s, free):
    """The lines the panel cycles through."""
    if state == "idle":
        return ["LEDIG"]
    t = [LABELS[state], "%d min" % ((left_s + 59) // 60) if left_s >= 60 else "%d s" % left_s]
    if free:
        t.append("til " + free)
    return t


def scroll(x, dt_ms, unit):
    """Move the ticker left by dt_ms worth of SPEED, wrapping after one text width + GAP."""
    x -= SPEED * dt_ms / 1000
    return x + unit if x <= -unit else x


def run():
    import sys
    import select
    import time
    from galactic import GalacticUnicorn
    from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

    gu = GalacticUnicorn()
    g = PicoGraphics(DISPLAY)
    gu.set_brightness(0.4)
    black = g.create_pen(0, 0, 0)
    # A: timer, coloured panel. B: timer, glowing text. C/D: fixed signs from SIGNS.
    mode = "A"
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)

    state, left_ms, free, since = "idle", 0, "", time.ticks_ms()
    x, last = 0, time.ticks_ms()
    while True:
        for name in "ABCD":
            if gu.is_pressed(getattr(GalacticUnicorn, "SWITCH_" + name)):
                mode = name
        step = (0.01 if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP) else 0) - \
               (0.01 if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN) else 0)
        if step:
            # ceiling: a full coloured panel above ~0.6 draws more than a PC USB port gives
            gu.set_brightness(min(0.6, max(0.05, gu.get_brightness() + step)))

        if poll.poll(0):
            msg = parse(sys.stdin.readline())
            if msg:
                state, left, free = msg
                left_ms, since = left * 1000, time.ticks_ms()

        now = time.ticks_ms()
        dt, last = time.ticks_diff(now, last), now
        remaining = left_ms if state == "paused" else max(0, left_ms - time.ticks_diff(now, since))
        if state in ("focus", "break") and remaining == 0:
            state = "idle"

        lines = texts(state, (remaining + 999) // 1000, free)
        text = "   ".join(lines)
        r, gr, b = COLOURS[state]
        if mode in SIGNS:  # signs always glow: a full white panel would overload the USB port
            text, (r, gr, b) = SIGNS[mode]
        elif state == "paused":  # pulse so a paused session reads differently from a break
            k = 0.35 + 0.65 * abs((now // 20) % 100 - 50) / 50
            r, gr, b = int(r * k), int(gr * k), int(b * k)

        colour = g.create_pen(r, gr, b)
        glow = mode != "A"
        g.set_pen(black if glow else colour)
        g.clear()
        g.set_pen(colour if glow else black)
        g.set_font("bitmap8")
        w = g.measure_text(text, 1)
        if w <= GalacticUnicorn.WIDTH:  # fits: stand still in the middle
            g.text(text, (GalacticUnicorn.WIDTH - w) // 2, 2, -1, 1)
        else:  # too wide: run as a ticker, drawn twice so the next pass follows straight on
            x = scroll(x, dt, w + GAP)
            g.text(text, int(x), 2, -1, 1)
            g.text(text, int(x) + w + GAP, 2, -1, 1)
        gu.update(g)
        time.sleep(0.02)  # the USB serial link stalls if the loop never sleeps


if __name__ == "__main__":
    run()
