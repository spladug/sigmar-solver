import cv2
import numpy

from keras.models import load_model

from sigmar.hex import Point, Orientation, Layout
from sigmar.board import Board, Element


def normalize_image(image):
    """Apply some basic image normalization to cut down on noise."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))

    image = image[0:38, 0:45]  # normalize slightly different image sizes
    image = clahe.apply(image)
    image = cv2.Canny(image, 150, 200)
    return image


def flatten_image_array(images):
    """Turn raw image data into data Tensorflow likes."""
    images = numpy.array(images)
    images = images.reshape(len(images), numpy.prod(images[0].shape))
    images = images.astype("float32")
    images /= 255
    return images


def detect_board(image):
    """Use a trained model to scrape a board's state from a screenshot."""
    model = load_model("elements.h5")

    board = Board.new()
    layout = Layout(Orientation.POINTY, Point(38, 38), Point(1100, 516))

    grayscale = image.convert("L")
    for i, (h, el) in enumerate(board.tiles):
        poly = list(layout.polygon_corners(h))
        cropped = grayscale.crop((poly[3].x+10, poly[3].y, poly[0].x-10, poly[0].y))
        normalized = normalize_image(numpy.array(cropped))
        prediction, = model.predict_classes(flatten_image_array([normalized]))
        el = Element(prediction)
        if el is not Element.EMPTY:
            board.set(h, el)

    return board, layout
