import keras
from flask import Flask, request
from flask_cors import CORS, cross_origin
import tensorflow_hub as hub
import keras.utils as image
from keras.applications.mobilenet import preprocess_input
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from io import BytesIO
import tensorflow as tf

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

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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
  # Process the image file using the Keras model.
  predicted_classes = process_image(image_file.filename)

  return { "class": predicted_classes }
  # return 'Image file uploaded successfully.', 200

if __name__ == '__main__':
  app.run(port=3000,host="0.0.0.0")
  print('Ready')
