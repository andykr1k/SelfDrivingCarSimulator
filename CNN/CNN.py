from tensorflow.keras import layers, models, regularizers
from PIL import Image
import numpy as np
import pygame
from tensorflow.keras.optimizers import Adam

def CNN_Predict(frame):
    img = np.array(frame)
    image_height, image_width = frame.size

    model = models.Sequential([
        layers.Conv2D(128, (3, 3), activation='relu', input_shape=(
            image_height, image_width, 1)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(40, activation='relu'),
        layers.Dropout(0.6),
        layers.Dense(4, activation='sigmoid')
    ])

    model.load_weights('./models/CNN/CNN_steering_model_auto_gs_64_1epoch_sig_bc.h5')

    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    test_image = img.reshape(1, image_height, image_width, 1)
    prediction = list(model.predict(test_image))
    prediction = np.squeeze(prediction)
    steering_vector = [float(x) for x in prediction]
    print(f'Predition: {steering_vector}')
    return steering_vector
