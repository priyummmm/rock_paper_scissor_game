# rock_paper_scissor_game
1. Introduction
This report documents Wind Valley, a desktop implementation of the classic Rock, Paper, Scissors
game, built entirely in Python using the standard-library Tkinter GUI toolkit. Rather than a plain,
utilitarian interface, the project explores a soft, pastel, storybook-like visual direction inspired by Studio
Ghibli films — hand-drawn-feeling skies, drifting clouds, rolling hills, and warm wooden panels — with
the computer opponent playfully named "Totoro".
The goal of this report is to walk through the source file, ghibli_rps.py, section by section and line by
line, explaining what each part of the code does and why it was written that way.
2. Objective
• Build a fully working Rock, Paper, Scissors game with a graphical interface.
• Practice GUI programming fundamentals using Tkinter (widgets, layout, events).
• Apply custom Canvas drawing to create original background art instead of using images.
• Implement simple animation (cloud drift, result-text pulse) using Tkinter's event loop.
• Manage application state cleanly: scores, round count, and round history.
3. Tools & Technologies Used
Component Technology / Library
Programming language Python 3
GUI toolkit Tkinter (Python standard library)
Graphics Tkinter Canvas (vector shapes: rectangles, ovals, polygons)
Randomness Python's built-in random module
Math utilities Python's built-in math module (used for hill wave curves)
External dependencies None — runs with a stock Python installation
4. Program Structure Overview
The program is organised as a single class, GhibliRPS, which extends tk.Tk (the main application
window). The class is broadly divided into four groups of methods:
• Setup — __init__, which configures the window and calls the builder methods.
• Scenery / drawing helpers — methods that paint the sky, sun, clouds, and hills onto a Canvas.
• UI construction — methods that create and place labels, buttons, and panels.
• Game logic — methods that decide the winner, update the score, and reset the game.
