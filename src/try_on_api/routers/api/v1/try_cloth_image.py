import time
import os
from loguru import logger
from try_on_api.utils import heybeauty_tryon
import aiohttp
import aiofiles
from fastapi import APIRouter, Body, File, HTTPException, UploadFile, status
from pydantic import UUID4

try_cloth_image_router = APIRouter(prefix="/tryon-image", tags=["Tryon Clothing Image"])


async def download_image(url: str, save_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error downloading image: {response.status}",
                )
            async with aiofiles.open(save_path, "wb") as file:
                await file.write(await response.read())
    return save_path


@try_cloth_image_router.post("/", status_code=status.HTTP_201_CREATED)
async def try_cloth(
    category: str = Body(...),
    cloth_img_url: str = Body(...),
    user_img_file: UploadFile = File(...),
):
    try:
        logger.info(
            "request triggered, cloth_img_url: {cloth_img_url}, category: {category}"
        )

        # Create temporary files to store the images
        user_img_path = f"/tmp/user_img_{int(time.time())}.jpg"
        cloth_img_path = f"/tmp/cloth_img_{int(time.time())}.jpg"

        logger.info("saving user image and downloading cloth image...")

        # Save the uploaded user image
        async with aiofiles.open(user_img_path, "wb") as user_file:
            await user_file.write(await user_img_file.read())

        # Download and save the cloth image from URL
        save_path = await download_image(cloth_img_url, cloth_img_path)

        logger.info(f"Image downloaded from {cloth_img_url} to {save_path}")

        # Generate output path
        output_path = f"/tmp/output_{int(time.time())}.jpg"

        logger.info("calling try on function...")
        result = await heybeauty_tryon(
            output_path=output_path,
            user_img_path=user_img_path,
            cloth_img_path=cloth_img_path,
            category=category,
        )

        # Clean up temporary files
        os.remove(user_img_path)
        os.remove(cloth_img_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
