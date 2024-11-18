from deepface import DeepFace
def gender_detection(image_path):
  objs = DeepFace.analyze(
    img_path=image_path,
    actions=['gender'],
  )
  return objs
