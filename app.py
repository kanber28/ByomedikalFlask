from flask import Flask, flash
from flask import render_template, url_for, json, request
import numpy as np
import librosa
import pandas as pd
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from tensorflow import keras
from flaskext.mysql import MySQL
import datetime
import os


mysql  = MySQL()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.run(debug=True)
app.config.update(
    TESTING=True,
    SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'acildurum'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'file'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()


@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template('index.html')


@app.route('/getStatus', methods=['GET', 'POST'])
def getstatus():
    status = request.args.get('status')
    if status == 'safe':
        cursor.execute("DELETE FROM isdanger WHERE human_id ='12'")
        conn.commit()
    elif status == 'danger':
        cursor.execute("INSERT INTO isdanger(human_id , alert_date , danger_type) VALUES(%s, %s, %s)", ("12", '2022-01-16 18:51:58', 'danger'))
        conn.commit()
    elif status == 'enkaz':
        cursor.execute("INSERT INTO isdanger(human_id , alert_date , danger_type) VALUES(%s, %s, %s)", ("12", '2022-01-16 18:51:58', 'enkaz'))
        conn.commit()
    else:
        pass

    return status


@app.route('/fileUpload', methods=['POST', 'GET'])
def fileupload():
    if request.method == 'POST':
        f = request.files['file']
        # f.save(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        return 'file uploaded successfully'


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        cursor.execute("UPDATE emergency_codes SET content=%s WHERE id=12",(str(request.form.get('emergency_code'))))
    cursor.execute("SELECT * FROM humans WHERE id=12")
    humanInfo = cursor.fetchone()
    cursor.execute("SELECT * FROM diseases WHERE humans_id=12")
    dicases = cursor.fetchone()
    cursor.execute("SELECT * FROM emergency_codes WHERE humans_id=12")
    emergency = cursor.fetchone()
    return render_template('profile.html', humanInfo=humanInfo, dicases=dicases, emergency=emergency)


@app.route('/modelResult', methods=['GET', 'POST'])
def model():
    if request.method == 'POST':
        f = request.files['file']
        # f.save(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))

    extracted_features_df = pd.read_csv('soundFeature.csv')
    X = np.array(extracted_features_df['feature'].tolist())
    y = np.array(extracted_features_df['class'].tolist())
    labelencoder = LabelEncoder()
    y = to_categorical(labelencoder.fit_transform(y))
    model = keras.models.load_model('lastTrainedModel.h5')

    filename = 'file/'+f.filename
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
    os.remove(filename)
    return render_template('index.html', result=prediction_class[0])
