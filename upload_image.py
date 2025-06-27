import uuid

from dotenv import load_dotenv

load_dotenv()
import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api

config = cloudinary.config(secure=True)


def upload_image(file):
    public_id =str(uuid.uuid4())
    cloudinary.uploader.upload(file, public_id=public_id)
    srcURL = CloudinaryImage(public_id).build_url()
    return srcURL



