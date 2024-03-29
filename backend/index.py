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

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = "secret_key"  # Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database file
db = SQLAlchemy(app)

# User model for the database
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(100), unique=True)
  name = db.Column(db.String(100))
  password = db.Column(db.String(100))
  age = db.Column(db.String(100))
  strings = db.Column(db.String)

  def __repr__(self):
      return '<User %r>' % self.name

  # Use these methods to handle the conversion between list and string
  def set_strings(self, string_list):
    self.strings = ";".join(string_list)

  def get_strings(self):
    return self.strings.split(";") if self.strings else []

  def __init__(self, username, name, age, password):
    self.username = username
    self.password = password
    self.name = name
    self.age = age

# Route for registration (accepts only POST requests)
@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
      return 'ok'
    user_data = request.get_json()
    username = user_data.get('username')
    password = user_data.get('password')
    name = user_data.get('name')
    age = user_data.get('age')
    # Check if the username already exists in the database
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return "exists"
    # Create a new user and add it to the database
    new_user = User(username, name, age, password)
    db.session.add(new_user)
    db.session.commit()
    return "ok"

# Route for login (accepts only POST requests)
@app.route('/login', methods=['POST'])
def login():
    user_data = request.get_json()
    username = user_data.get('username')
    password = user_data.get('password')
    # Check if the username and password match a user in the database
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        # Store the user's username in the session
        return user.name
    else:
        return "not-found-error"

def decode_img(img):
  img = tf.image.decode_jpeg(img, channels=3)
  img = tf.image.convert_image_dtype(img, tf.float32)
  # resize the image to the desired size.
  return tf.image.resize(img, [28, 28])

def process_path(filepath):
  # load the raw data from the file as a string
  img = tf.io.read_file(filepath)
  img = decode_img(img)
  return img


def process_image(image_file):
  print(image_file)
  # Load the Keras model from a saved model file.
  model = keras.models.load_model('./model-v2.h5', custom_objects={'KerasLayer': hub.KerasLayer})

  # Preprocess the image file to match the input requirements of the model.
  img = tf.keras.preprocessing.image.load_img(image_file, target_size=(28, 28))
  img_array = tf.keras.preprocessing.image.img_to_array(img)
  img_array = preprocess_input(img_array)
  img_array = tf.expand_dims(img_array, 0)  # Expand dimensions to match the input shape of the model

  # Pass the preprocessed image to the model and get the predictions.
  predictions = model.predict(img_array)
  class_names = ["Actinic keratoses", "Basal cell carcinoma", "Benign keratosis-like lesions", "Dermatofibroma", "Melanocytic nevi", "Vascular lesions", "Melanoma"]
  print(predictions)

  # Interpret the predictions to determine the model's predicted classes.
  predicted_classes = [class_names[i] for i in np.argmax(predictions, axis=1)]
  return predicted_classes[0]

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
    strings = user.get_strings()
    strings.append(file_path)
    user.set_strings(strings)

    # Commit the changes to the database
    db.session.commit()

  # Process the image file using the Keras model.
  predicted_classes = process_image(image_file.filename)

  return { "class": predicted_classes }
  # return 'Image file uploaded successfully.', 200

# Create an application context
with app.app_context():
  db.create_all()  # create tables

  # Query all users and print
  users = User.query.all()
  for user in users:
      print(f'User ID: {user.id}, Name: {user.name}, Username: {user.username}, Password: {user.password}, Strings: {user.get_strings()}')


if __name__ == '__main__':
  app.run(port=3000,host="0.0.0.0")
  print('Ready')
