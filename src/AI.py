from tensorflow.keras import layers, models, regularizers
from PIL import Image
import numpy as np
import pygame
from tensorflow.keras.optimizers import Adam

def CNN_Predict(frame):
    image_data = pygame.surfarray.array3d(frame)
    image_height, image_width, num_channels = image_data.shape

    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(
            image_height, image_width, num_channels)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu',
                      kernel_regularizer=regularizers.l2(0.001)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu',
                      kernel_regularizer=regularizers.l2(0.001)),
        layers.Flatten(),
        layers.Dense(64, activation='relu',
                     kernel_regularizer=regularizers.l2(0.001)),
        layers.Dropout(0.6),
        layers.Dense(4, activation='sigmoid')
    ])
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mae')

    model.load_weights('./models/CNN_steering_model.h5')

    test_image = image_data.reshape(1, image_height, image_width, num_channels)
    prediction = list(model.predict(test_image))
    prediction = np.squeeze(prediction)
    steering_vector = [int(x) for x in prediction]
    print(f'Predition: {steering_vector}')
    return steering_vector
