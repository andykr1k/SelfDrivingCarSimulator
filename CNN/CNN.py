import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
import numpy as np
from tensorflow.keras.optimizers.legacy import Adam

def CNN_Predict(frame):
    img = np.array(frame)
    image_height, image_width = frame.size

    model = models.Sequential([
        layers.Conv2D(64, (3, 3), activation='relu', input_shape=(
            64, 64, 1)),
        layers.MaxPooling2D(),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D(),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D(),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D(),
        layers.BatchNormalization(),
        layers.Flatten(),
        layers.Dense(40, activation='relu'),
        layers.Dropout(0.6),
        layers.Dense(4, activation='sigmoid')
    ])

    model.load_weights(
        './models/CNN/CNN_steering_model_manual_gs_CMBx4_10epoch_sig_bc.h5')

    optimizer = Adam(learning_rate=0.001)


    model.compile(optimizer=optimizer, loss='binary_crossentropy',
              metrics=[tf.keras.metrics.BinaryAccuracy()])

    test_image = img.reshape(1, image_height, image_width, 1)
    prediction = list(model.predict(test_image))
    prediction = np.squeeze(prediction)
    steering_vector = [float(x) for x in prediction]
    print(f'Predition: {steering_vector}')
    return steering_vector
