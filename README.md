# Solver for Sigmar's Garden

This is a dumb, hacky, WIP solver for Sigmar's Garden which is the
mini-game in [Opus Magnum].

It works in a few steps:

1. Take a screenshot of the game.
2. Build a model of the game state using image classification.
3. Solve the game with a simple depth-first search.
4. Click buttons to actually execute the solution.
5. Rinse and repeat.

## Requirements

* Python 3.6
* This runs on Windows only at the moment. (It uses win32 APIs directly).

## Initial setup

You'll need to train the image classifier before getting started.

1. Start Opus Magnum and open up Sigmar's Garden.
2. `python -m sigmar.vision.training generate`
3. Manually categorize the generated images into the provided folders.
4. `python -m sigmar.vision.training train`

[Opus Magnum]: http://www.zachtronics.com/opus-magnum/
