from cv2 import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from tensorflow.keras import models, layers, utils

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    # Change into data directory
    os.chdir(data_dir)
    images = []
    labels = []

    # Repeat as many times as categories exist
    for i in range(NUM_CATEGORIES):

        # Enter "i"'th folder
        path = os.path.join(os.getcwd(), str(i))
        os.chdir(path)

        # Get all images in folder
        files = os.listdir('.')

        # For each image, add it to images array
        for image in files:
            
            # Read image and convert it to RGB from BGR
            img = cv2.imread(image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # If not correct size, resize image
            shape = img.shape
            if shape != (IMG_HEIGHT, IMG_WIDTH, 3):
                img = cv2.resize(img, (IMG_HEIGHT, IMG_WIDTH))

            # Update arrays
            images.append(img)
            labels.append(i)

        # Go back to data folder
        os.chdir("..")

    return(images, labels)




def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    
    # Create empty sequential Keras model
    model = tf.keras.models.Sequential()

    # If no conv. layer: simply specify input layer and input shape
    # model.add(layers.Input(shape=(IMG_WIDTH, IMG_HEIGHT, 3)))

    # Add 2D Convolutional Layer (Filtering) with 32 filters, a 3 by 3 kernel to use, 
    # ReLu activation function, using input_shape specified
    model.add(layers.Conv2D(
        32, (3,3), activation='relu', input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
    ))

    # Add a 2D Max Pooling Layer, which takes the maximum valued pixel every 2 by 2 square, thus reducing image size 
    model.add(layers.MaxPooling2D(pool_size=(2,2)))

    model.add(layers.Conv2D(
        64, (3,3), activation='relu', input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
    ))
    # Flatten layer data from 2D to 1D, get ready for output
    model.add(layers.Flatten())

    # Add hidden layer with dropout
    model.add(layers.Dense(128, activation="relu"))
    # COMMENT: Dropout seems to decrease accuracy to ~5%... issue?
    # model.add(layers.Dropout(0.2))

    # Add output layer with NUM_CATEGORIES outputs and softmax algorithm
    model.add(layers.Dense(NUM_CATEGORIES, activation="softmax"))

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
