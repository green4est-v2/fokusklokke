# Fokusklokke

Pomodoro timer (`index.html`, served by GitHub Pages) that drives a Pimoroni Galactic Unicorn (Pico 2 W, MicroPython) over USB with Web Serial.

- No build step, no dependencies. `index.html` stays a single self-contained file.
- UI text is Norwegian (bokmål).
- History lives in the browser's localStorage (`stepdown-timer-v1`). Changing its shape without a migration loses the user's data.
- The repo is public: no secrets, names or work data in it.
- Anything read from the serial port is untrusted input: parse defensively, never pass it to `innerHTML` or `eval`.

@AGENTS.md
