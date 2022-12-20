import keras
from flask import Flask, request
import tensorflow_hub as hub
import keras.utils as image
from keras.applications.mobilenet import preprocess_input
from keras.preprocessing.image import ImageDataGenerator

from io import BytesIO

def preprocess_image(image_file):
  # Convert the image from a binary file to a 3-dimensional tensor.
  image_tensor = image.load_img(image_file, target_size=(224, 224))

  # create an instance of the ImageDataGenerator class
  datagen = ImageDataGenerator(
    rescale=1./255,  # rescale the pixel values from 0-255 to 0-1
    rotation_range=40,  # randomly rotate the image by up to 40 degrees
    width_shift_range=0.2,  # randomly shift the image horizontally by up to 20%
    height_shift_range=0.2,  # randomly shift the image vertically by up to 20%
    shear_range=0.2,  # apply random shearing transformations
    zoom_range=0.2,  # randomly zoom in on the image
    horizontal_flip=True,  # randomly flip the image horizontally
    fill_mode='nearest'  # fill in any newly created pixels after the transformation with the nearest pixel
  )
  # Resize the image tensor to match the input size of the model.
  resized_image = datagen.flow(image_tensor)

  # Normalize the pixel values in the image tensor.
  normalized_image = preprocess_input(resized_image)

  return normalized_image
# from werkzeug.utils import secure_filename

app = Flask(__name__)

def process_image(image_file):
  print(image_file)
  # Load the Keras model from a saved model file.
  model = keras.models.load_model('./model.h5', custom_objects={'KerasLayer':hub.KerasLayer})

  # Preprocess the image file to match the input requirements of the model.
  preprocessed_image = preprocess_image(image_file)

  # Pass the preprocessed image to the model and get the predictions.
  predictions = model.predict(preprocessed_image)

  # Interpret the predictions to determine the model's predicted classes.
  predicted_classes = interpret_predictions(predictions)

  return predicted_classes

@app.route('/model-output', methods=['POST'])
def upload_image():
  # Get the image file from the request.
  
  image_file = request.files['file']
  print(image_file)
  # Check if the image file is present in the request.
  if not image_file:
    return 'No image file provided.', 400

  # Process the image file using the Keras model.
  predicted_classes = process_image(BytesIO(image_file.read()))

  return 'Image file uploaded successfully.', 200

if __name__ == '__main__':
  app.run(port=3000)
  print('Ready')