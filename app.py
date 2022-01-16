from flask import Flask, flash
from flask import render_template, url_for
import numpy as np
import librosa
import pandas as pd
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from tensorflow import keras


app = Flask(__name__, template_folder='templates', static_folder='static')
app.run(debug=True)
app.config.update(
    TESTING=True,
    SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template('index.html')


@app.route('/za', methods=['GET', 'POST'])
def model():
    extracted_features_df = pd.read_csv('soundFeature.csv')
    X = np.array(extracted_features_df['feature'].tolist())
    y = np.array(extracted_features_df['class'].tolist())
    labelencoder = LabelEncoder()
    y = to_categorical(labelencoder.fit_transform(y))
    model = keras.models.load_model('lastTrainedModel.h5')

    filename = 'test.wav'
    # filename="./UrbanSound8K/audio/fold1/7061-6-0-0.wav"
    audio, sample_rate = librosa.load(filename, res_type='kaiser_fast')
    mfccs_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    mfccs_scaled_features = np.mean(mfccs_features.T, axis=0)

    # print(mfccs_scaled_features)
    mfccs_scaled_features = mfccs_scaled_features.reshape(1, -1)
    # print(mfccs_scaled_features)
    # print(mfccs_scaled_features.shape)
    predicted_label = model.predict_classes(mfccs_scaled_features)
    # print(predicted_label)
    prediction_class = labelencoder.inverse_transform(predicted_label)
    return prediction_class[0]
