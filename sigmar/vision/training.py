import glob
import random
import sys
import time
import os
import errno

import numpy
import cv2

from keras.utils.np_utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense

from sigmar.board import Board, Element
from sigmar.hex import Point, Orientation, Layout
from sigmar.windows import get_screenshot, set_window_foreground, click_new_game
from sigmar.vision import normalize_image, flatten_image_array


def ensure_path(path):
    """Create a directory if it doesn't exist."""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def capture_tile_images():
    """Screenshot Sigmar's Garden and save images of each tile location to disk for manual classification."""
    image = get_screenshot()

    board = Board.new()
    layout = Layout(Orientation.POINTY, Point(38, 38), Point(1100, 516))

    ts = int(time.time())
    for i, (h, el) in enumerate(board.tiles):
        poly = list(layout.polygon_corners(h))
        cropped = image.crop((poly[3].x+10, poly[3].y, poly[0].x-10, poly[0].y))
        cropped.save(f"training/{ts}-{i}.png")


def generate_raw_images():
    """Capture tile images from multiple games of Sigmar's Garden to get different marble positions and lighting."""
    ensure_path("training/")
    for el in Element:
        ensure_path(f"training/{el.name}")

    for i in range(1):
        set_window_foreground()
        click_new_game()
        capture_tile_images()

    print("Training images have been collected in training/. Please manually place them into the provided folders.")


def load_label(name):
    """Load all images classified as a specific label (element)."""
    images = []

    for image_filename in glob.glob(f"training/{name}/*.png"):
        image = cv2.imread(image_filename, 0)
        image = normalize_image(image)
        images.append(image)

    random.shuffle(images)
    partition_point = int(len(images) * .8)
    return images[:partition_point], images[partition_point:]


def train_model():
    """Use human classified images to train a neural net to classify Sigmar's Garden marbles."""
    training_data, training_labels = [], []
    test_data, test_labels = [], []

    print("Loading all labels...")
    for el in Element:
        print(f"  Loading {el.name}...")
        training_images, test_images = load_label(el.name.upper())

        training_data.extend(training_images)
        training_labels += [el.value] * len(training_images)

        test_data.extend(test_images)
        test_labels += [el.value] * len(test_images)

    training_data = flatten_image_array(training_data)
    training_labels = to_categorical(numpy.array(training_labels))

    test_data = flatten_image_array(test_data)
    test_labels = to_categorical(numpy.array(test_labels))

    model = Sequential()
    model.add(Dense(512, activation='relu', input_shape=(len(training_data[0]),)))
    model.add(Dense(512, activation='relu'))
    model.add(Dense(len(Element), activation='softmax'))
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

    model.fit(
        training_data,
        training_labels,
        batch_size=256,
        epochs=5,
        verbose=1,
        validation_data=(test_data, test_labels),
    )

    [test_loss, test_acc] = model.evaluate(test_data, test_labels)
    print(f"Evaluation result on Test Data : Loss = {test_loss}, accuracy = {test_acc}")
    model.save("elements.h5")


def main():
    commands = {
        "generate": generate_raw_images,
        "train": train_model,
    }

    try:
        choice = sys.argv[1]
        fn = commands[choice]
    except (IndexError, KeyError):
        print(f"USAGE: python -m sigmar.vision.training {{{','.join(commands.keys())}}}")
        sys.exit(1)

    fn()


if __name__ == "__main__":
    main()
