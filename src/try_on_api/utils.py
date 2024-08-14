import requests
import base64
import os
from PIL import Image
import io
from loguru import logger
from try_on_api.config import Config

def apply_exif_rotation(image: Image.Image) -> Image.Image:
    """
    Apply EXIF rotation to the input image.
    """
    if hasattr(image, "_getexif"):
        exif = image._getexif()
        if exif:
            orientation = exif.get(274)
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    return image


def heybeauty_tryon(user_img_path, cloth_img_path, category, output_path, caption=None):
    logger.info('entered the ufunction')
    base_url = "https://heybeauty.ai/api"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.API_KEY}",
    }
    
    logger.info(f"Using API key: {Config.API_KEY[:5]}...{Config.API_KEY[-5:]}")
    logger.info(f"Full headers: {headers}")


    logger.info('creating task data')
    create_task_data = {
        "user_img_name": os.path.basename(user_img_path),
        "cloth_img_name": os.path.basename(cloth_img_path),
        "category": category,
    }
    if caption:
        create_task_data["caption"] = caption
        
    logger.info('hitting create-task endpoint')

    response = requests.post(
        f"{base_url}/create-task", headers=headers, json=create_task_data
    )
    
    logger.info(f"create_task_data: {create_task_data}, response: {response.text}")
    if response.status_code != 200:
        raise Exception(f"Failed to create task: {response.text}")

    task_data = response.json()["data"]
    task_uuid = task_data["uuid"]
    user_img_url = task_data["user_img_url"]
    cloth_img_url = task_data["cloth_img_url"]
    
    logger.info(f"task_data: {task_data}, uuid: {task_uuid}, user_img_url: {user_img_url}, cloth_img_url: {cloth_img_url}")

    with Image.open(user_img_path) as img:
        img = apply_exif_rotation(img)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()
        requests.put(user_img_url, data=img_byte_arr)

    # Cloth image
    with Image.open(cloth_img_path) as img:
        img = apply_exif_rotation(img)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()
        requests.put(cloth_img_url, data=img_byte_arr)

    submit_task_data = {"task_uuid": task_uuid}
    response = requests.post(
        f"{base_url}/submit-task", headers=headers, json=submit_task_data
    )
    if response.status_code != 200:
        raise Exception(f"Failed to submit task: {response.text}")

    response = requests.post(
        f"{base_url}/get-task-info", headers=headers, json={"task_uuid": task_uuid}
    )

    if response.status_code != 200:
        raise Exception(f"Failed to query task: {response.text}")

    task_info = response.json()["data"]
    status = task_info["status"]

    if status == "successed":
        # Download and save the output image
        output_url = task_info["tryon_img_url"]
        response = requests.get(output_url)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            with Image.open(output_path) as img:
                width, height = img.size

                left = 0
                upper = 0
                right = width
                lower = height - 50

                cropped_img = img.crop((left, upper, right, lower))
                cropped_img.save(output_path)

            with open(output_path, "rb") as image_file:
                img_base64 = base64.b64encode(image_file.read()).decode("utf-8")

            return img_base64
        else:
            raise Exception(
                f"Failed to download the output image: {response.status_code}"
            )
    elif status == "failed":
        raise Exception(f"Try-On task failed: {task_info['err_msg']}")
    else:
        raise Exception("Unexpected error occurred")