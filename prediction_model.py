import json
import numpy as np
import os
import keras

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
from keras.utils import to_categorical
from dollar_recognizer.recognizer import NUM_POINTS
from sklearn.model_selection import train_test_split
from scipy.signal import resample
from tqdm.notebook import tqdm
import xml.etree.ElementTree as ET
from sklearn.preprocessing import LabelEncoder, StandardScaler

THREE_GESTURES = ['pigtail', 'carret', 'x']

folder_path = 'saved_model_params'
model_file = os.path.join(folder_path, 'gesture_model.json')
weights_file = os.path.join(folder_path, 'gesture_model.weights.h5')
label_file = os.path.join(folder_path, 'label_names.json')

class PredictionModel:
    def __init__(self, model_loaded) -> None:
        
        if not model_loaded:
            data = self.load_data('dataset/xml_logs/s02', '')
            X_train, X_test, y_train, y_test, labels, self.encoder = self.prepare_data(data)
            self.model, self.history = self.create_model(X_train, X_test, y_train, y_test, labels)
            
            self.save_model(self.model, THREE_GESTURES)
        else:
            self.model = self.load_gesture_model(model_file, weights_file)

        self.encoder = LabelEncoder()
        self.labels = THREE_GESTURES
        self.labels_encoded = self.encoder.fit_transform(self.labels)

    def save_model(self, model, label_names):
        model_json = model.to_json()
        with open(model_file, 'w') as json_file:
            json_file.write(model_json)

        model.save_weights(weights_file)

        with open(label_file, 'w') as json_file:
            json.dump(label_names, json_file)

    @staticmethod
    def load_gesture_model(model_path, weights_path, custom_objects=None):
        print('Loading model …')
        with open(model_path, 'r') as json_file:
            loaded_model_json = json_file.read()
        model = keras.models.model_from_json(loaded_model_json, custom_objects=custom_objects)
        model.load_weights(weights_path)
        return model

    def load_data(self, folder, subfolder):
        data = []

        for root, subdirs, files in os.walk(folder):
            if 'ipynb_checkpoint' in root:
                continue

            if len(files) > 0:
                for f in tqdm(files):
                    if '.xml' in f:
                        fname = f.split('.')[0]
                        label = fname[:-2]

                        xml_root = ET.parse(f'{subfolder}{root}/{f}').getroot()

                        points = []
                        for element in xml_root.findall('Point'):
                            x = element.get('X')
                            y = element.get('Y')
                            points.append([x, y])

                        points = np.array(points, dtype=float)

                        scaler = StandardScaler()
                        points = scaler.fit_transform(points)

                        resampled = resample(points, NUM_POINTS)

                        if label in THREE_GESTURES:
                            data.append((label, resampled))
        return data

    def prepare_data(self, data):
        labels = [sample[0] for sample in data]
        print(set(labels))

        encoder = LabelEncoder()
        self.labels_encoded = encoder.fit_transform(labels)

        print(set(self.labels_encoded))
        y = to_categorical(self.labels_encoded)
        print(len(y[0]))

        sequences = [sample[1] for sample in data]
        X = np.array(sequences)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
        
        return X_train, X_test, y_train, y_test, labels, encoder

    def create_model(self, X_train, X_test, y_train, y_test, labels):
        model = Sequential()
        model.add(LSTM(32, input_shape=(NUM_POINTS, 2)))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(len(set(labels)), activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=0.0001)
        stop_early = EarlyStopping(monitor='val_loss', patience=3)
        
        history = model.fit(
            X_train,
            y_train,
            epochs=50,
            batch_size=100,
            validation_data=(X_test, y_test),
            verbose=1,
            callbacks=[reduce_lr, stop_early]
        )
        
        model.summary()
        
        return model, history

    def predict_gesture(self, gesture):
        scaler = StandardScaler()
        gesture = scaler.fit_transform(gesture)
        gesture = resample(gesture, NUM_POINTS)
        prediction = self.model.predict(np.array([gesture]))
        prediction = np.argmax(prediction)
        prediction_label = self.encoder.inverse_transform(np.array([prediction]))[0]
        return prediction_label
        

