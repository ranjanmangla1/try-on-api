import requests
import base64
import os
from PIL import Image
import aiohttp
import aiofiles
import time
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


async def heybeauty_tryon(
    user_img_path, cloth_img_path, category, output_path, caption=None
):
    logger.info("entered the ufunction")
    base_url = "https://heybeauty.ai/api"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.API_KEY}",
    }

    logger.info(f"Using API key: {Config.API_KEY[:5]}...{Config.API_KEY[-5:]}")
    logger.info(f"Full headers: {headers}, category: {category}")

    logger.info("creating task data")
    create_task_data = {
        "user_img_name": os.path.basename(user_img_path),
        "cloth_img_name": os.path.basename(cloth_img_path),
        "category": str(category),
    }
    if caption:
        create_task_data["caption"] = caption

    logger.info(f"hitting create-task endpoint, create task data: {create_task_data}")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{base_url}/create-task", headers=headers, json=create_task_data
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to create task: {await response.text()}")
            task_data = (await response.json())["data"]

    logger.info(
        f"create_task_data: {create_task_data}, response: {response.text}, task_data: {task_data}"
    )
    # task_data = response.json()["data"]
    task_uuid = task_data["uuid"]
    user_img_url = task_data["user_img_url"]
    cloth_img_url = task_data["cloth_img_url"]

    logger.info(
        f"task_data: {task_data}, \nuuid: {task_uuid}, user_img_url: {user_img_url}, \ncloth_img_url: {cloth_img_url}"
    )

    async with aiofiles.open(user_img_path, "rb") as f:
        user_img_data = await f.read()
    async with aiohttp.ClientSession() as session:
        async with session.put(user_img_url, data=user_img_data) as response:
            # if response.status != 200:
            #     raise Exception(f"Failed to upload user image: {await response.text()}")
            print(f"response.status: {response.status}")

    logger.info(f"uploaded image to {user_img_url}")

    # Upload cloth image
    async with aiofiles.open(cloth_img_path, "rb") as f:
        cloth_img_data = await f.read()
    async with aiohttp.ClientSession() as session:
        async with session.put(cloth_img_url, data=cloth_img_data) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to upload cloth image: {await response.text()}"
                )
            logger.info(f"response.status: {await response.text()}")

    submit_task_data = {"task_uuid": task_uuid}
    response = requests.post(
        f"{base_url}/submit-task", headers=headers, json=submit_task_data
    )
    # if response.status_code != 200:
    #     raise Exception(f"Failed to submit task: {response.text}")
    logger.info(f"response of submit task: {submit_task_data}")

    time.sleep(30)

    response = requests.post(
        f"{base_url}/get-task-info", headers=headers, json={"task_uuid": task_uuid}
    )

    task_info = response.json()["data"]

    print(f"task_info: {task_info}")

    output_url = task_info["tryon_img_url"]
    logger.info(f"output url: {output_url}")
    return output_url
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(output_url) as response:
    #         image_data = await response.read()
    #         async with aiofiles.open(output_path, "wb") as f:
    #             await f.write(image_data)

    #         # Process the image (crop, etc.)
    #         # Note: Image processing with PIL is not async, so we keep it as is
    #         with Image.open(output_path) as img:
    #             width, height = img.size
    #             cropped_img = img.crop((0, 0, width, height - 50))
    #             cropped_img.save(output_path)

    #         async with aiofiles.open(output_path, "rb") as image_file:
    #             img_base64 = base64.b64encode(await image_file.read()).decode("utf-8")
    #         logger.info(f"Final Result: {img_base64}")
    #         return img_base64
