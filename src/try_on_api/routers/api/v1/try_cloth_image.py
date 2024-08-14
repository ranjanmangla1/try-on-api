import time
import os
from loguru import logger
from try_on_api.utils import heybeauty_tryon
from try_on_api.config import Config

from fastapi import APIRouter, Body, File, HTTPException, UploadFile, status
from pydantic import UUID4


try_cloth_image_router = APIRouter(prefix="/tryon-image", tags=["Tryon Clothing Image"])


@try_cloth_image_router.post("/", status_code=status.HTTP_201_CREATED)
async def try_cloth(
    category: str = Body(...),
    user_img_file: UploadFile = File(...),
    cloth_img_file: UploadFile = File(...),
):
    try:
        logger.info('request triggered')
        # Create temporary files to store the uploaded images
        user_img_path = f"/tmp/user_img_{int(time.time())}.jpg"
        cloth_img_path = f"/tmp/cloth_img_{int(time.time())}.jpg"
        
        
        logger.info('opening saved files...')
        # Save the uploaded files
        with open(user_img_path, "wb") as user_file:
            user_file.write(await user_img_file.read())
        with open(cloth_img_path, "wb") as cloth_file:
            cloth_file.write(await cloth_img_file.read())
            
            
        
        # Generate output path
        output_path = f"/tmp/output_{int(time.time())}.jpg"
        
        logger.info('callign try on function...')
        result = heybeauty_tryon(
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