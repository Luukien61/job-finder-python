from deepface import DeepFace
def gender_detection(image_path):
  objs = DeepFace.analyze(
    img_path=image_path,
    actions=['gender'],
  )
  return objs

import cv2
import numpy as np

GENDER_MODEL = 'gender-weights/deploy_gender.prototxt'
GENDER_PROTO = 'gender-weights/gender_net.caffemodel'
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
GENDER_LIST = ['Male', 'Female']
FACE_PROTO = "gender-weights/deploy.prototxt.txt"
FACE_MODEL = "gender-weights/res10_300x300_ssd_iter_140000_fp16.caffemodel"
face_net = cv2.dnn.readNetFromCaffe(FACE_PROTO, FACE_MODEL)
gender_net = cv2.dnn.readNetFromCaffe(GENDER_MODEL, GENDER_PROTO)

frame_width = 1280
frame_height = 720


def get_faces(frame, confidence_threshold=0.5):
  # convert the frame into a blob to be ready for NN input
  blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177.0, 123.0))
  # set the image as input to the NN
  face_net.setInput(blob)
  # perform inference and get predictions
  output = np.squeeze(face_net.forward())
  # initialize the result list
  faces = []
  # Loop over the faces detected
  for i in range(output.shape[0]):
    confidence = output[i, 2]
    if confidence > confidence_threshold:
      box = output[i, 3:7] * \
            np.array([frame.shape[1], frame.shape[0],
                      frame.shape[1], frame.shape[0]])
      # convert to integers
      start_x, start_y, end_x, end_y = box.astype(int)
      # widen the box a little
      start_x, start_y, end_x, end_y = start_x - \
                                       10, start_y - 10, end_x + 10, end_y + 10
      start_x = 0 if start_x < 0 else start_x
      start_y = 0 if start_y < 0 else start_y
      end_x = 0 if end_x < 0 else end_x
      end_y = 0 if end_y < 0 else end_y
      # append to our list
      faces.append((start_x, start_y, end_x, end_y))
  return faces


def get_optimal_font_scale(text, width):
  """Determine the optimal font scale based on the hosting frame width"""
  for scale in reversed(range(0, 60, 1)):
    textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale / 10, thickness=1)
    new_width = textSize[0][0]
    if (new_width <= width):
      return scale / 10
  return 1


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):

  (h, w) = image.shape[:2]
  if width is None and height is None:
    return image
  # check to see if the width is None
  if width is None:
    r = height / float(h)
    dim = (int(w * r), height)
  # otherwise, the height is None
  else:
    r = width / float(w)
    dim = (width, int(h * r))
  # resize the image
  return cv2.resize(image, dim, interpolation=inter)


def predict_gender(input_path: str):
  img = cv2.imread(input_path)
  frame = img.copy()
  if frame.shape[1] > frame_width:
    frame = image_resize(frame, width=frame_width)
  faces = get_faces(frame)
  for i, (start_x, start_y, end_x, end_y) in enumerate(faces):
    face_img = frame[start_y: end_y, start_x: end_x]
    blob = cv2.dnn.blobFromImage(image=face_img, scalefactor=1.0, size=(
      227, 227), mean=MODEL_MEAN_VALUES, swapRB=False, crop=False)
    # Predict Gender
    gender_net.setInput(blob)
    gender_preds = gender_net.forward()
    i = gender_preds[0].argmax()
    gender = GENDER_LIST[i]
    gender_confidence_score = gender_preds[0][i]
    print(gender)
    print(gender_confidence_score)
    return gender

