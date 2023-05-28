import keras
from flask import Flask, render_template, request, redirect, session
from flask_cors import CORS, cross_origin
import tensorflow_hub as hub
import keras.utils as image
from keras.applications.mobilenet import preprocess_input
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from io import BytesIO
import tensorflow as tf
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = "secret_key"  # Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database file

# User model for the database
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(100), unique=True)
  name = db.Column(db.String(100))
  password = db.Column(db.String(100))
  age = db.Column(db.String(100))
  uploaded_files = db.Column(ARRAY(db.String), nullable=True)

  def __init__(self, username, name, age, password, uploaded_files=None):
    self.username = username
    self.password = password
    self.uploaded_files = uploaded_files

# Route for registration (accepts only POST requests)
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    # Check if the username already exists in the database
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return "Username already exists!"
    # Create a new user and add it to the database
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return "ok"

# Route for login (accepts only POST requests)
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    age = request.form['age']
    # Check if the username and password match a user in the database
    user = User.query.filter_by(username=username, name=name, age=age, password=password).first()
    if user:
        # Store the user's username in the session
        session['username'] = user.username
        return "ok"
    else:
        return "Invalid username or password!"

def decode_img(img):
  img = tf.image.decode_jpeg(img, channels=3)
  img = tf.image.convert_image_dtype(img, tf.float32)
  # resize the image to the desired size.
  return tf.image.resize(img, [299, 299])

def process_path(filepath):
  # load the raw data from the file as a string
  img = tf.io.read_file(filepath)
  img = decode_img(img)
  return img



def process_image(image_file):
  print(image_file)
  # Load the Keras model from a saved model file.
  model = keras.models.load_model('./model.h5', custom_objects={'KerasLayer':hub.KerasLayer})

  # Preprocess the image file to match the input requirements of the model.
  # preprocessed_image = preprocess_image(image_file)
  # preprocessed_image = image_file
  # Pass the preprocessed image to the model and get the predictions.
  print("Starting predictions")
  n_testing_samples = 1
  X_test = np.zeros((n_testing_samples, 299, 299, 3))
  X_test[0] = process_path(image_file)

  predictions = model.predict(X_test)
  class_names = ["benign", "malignant"]
  print(predictions)
  # Interpret the predictions to determine the model's predicted classes.
  # predicted_classes = interpret_predictions(predictions)

  threshold = 0.23
  value = predictions[0][0]

  if value >= threshold:
    return "maligant"
  else:
    return "benign"

  # return prections[0][0] #predicted_classes

@app.route('/model-output', methods=['POST'])
@cross_origin()
def upload_image():
  # Get the image file from the request.
  
  image_file = request.files['file']
  # print(image_file)
  # Check if the image file is present in the request.
  if not image_file:
    return 'No image file provided.', 400

  image_file.save(image_file.filename)

  username = request.form.get('username', '')

  # Get the user instance (assuming you have the user_id or username)
  user = User.query.filter_by(username=username).first()

  if user:
    # Add a new file path to the user's uploaded_files array
    file_path = image_file.filename
    user.uploaded_files.append(file_path)

    # Commit the changes to the database
    db.session.commit()

  # Process the image file using the Keras model.
  predicted_classes = process_image(image_file.filename)

  return { "class": predicted_classes }
  # return 'Image file uploaded successfully.', 200

if __name__ == '__main__':
  app.run(port=3000,host="0.0.0.0")
  print('Ready')
