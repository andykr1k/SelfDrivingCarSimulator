from tensorflow.keras import layers, models, regularizers
from PIL import Image
import numpy as np
import pygame
from tensorflow.keras.optimizers import Adam

def CNN_Predict(frame):
    img = np.array(frame)
    image_height, image_width = frame.size
    num_channels = len(frame.getbands())

    model = models.Sequential([
        layers.Conv2D(128, (3, 3), activation='relu', input_shape=(
            image_height, image_width, num_channels)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(40, activation='relu'),
        layers.Dropout(0.6),
        layers.Dense(4, activation='relu')
    ])

    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mse')

    model.load_weights('./models/CNN_steering_model_gs_64.h5')

    test_image = img.reshape(1, image_height, image_width, num_channels)
    prediction = list(model.predict(test_image))
    prediction = np.squeeze(prediction)
    steering_vector = [float(x) for x in prediction]
    print(f'Predition: {steering_vector}')
    return steering_vector
