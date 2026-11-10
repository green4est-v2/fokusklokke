# fokusklokke
Combining a self made pomodo app with a PICO 2 W galaxy unicorn that shows time left of focus at my work desk

## Setup

1. **Lamp program.** In VS Code with the MicroPico extension, connect the Galactic Unicorn over USB and upload `lampe/main.py` to the board as `main.py`. This replaces Pimoroni's demo launcher. Close the extension's connection afterwards, since only one program can use the USB port at a time.
2. **App.** Open the GitHub Pages site in Edge or Chrome and click **Koble til lampe** once. After that the app reconnects by itself whenever the lamp is plugged in.

What the lamp shows: red **FOKUS** with minutes left and when you're free, amber **PAUSE**, pulsing amber **VENT** when paused, green **LEDIG** otherwise. If the browser closes, the lamp keeps counting down and then shows LEDIG.

Buttons on the back: **A** coloured panel with dark text, **B** dark panel with glowing text, **C** a blue "OPPTATT" sign, **D** a white "Lunsj!" sign, **LUX +/−** brightness (hold to adjust). Press A or B to go back to the timer; it keeps counting in the background. Mode and brightness reset when the lamp loses power.

Test the lamp's message parser on a PC: `python lampe/test_main.py`
