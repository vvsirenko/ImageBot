import fal_client
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import json

load_dotenv()


class FalClient:

    def __init__(self):
        """Initialize the FalClient."""
        pass

    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(log["message"])

    async def subscribe(
        self,
        images_data_url: str | None = None,
        learning_rate: float = 0.00009,
        steps: int = 1000,
        multiresolution_training: bool = True,
        subject_crop: bool = True
    ):
        """
        Subscribe to the fal-ai/flux-lora-portrait-trainer model asynchronously.
        
        Args:
            images_data_url: URL of the images data
            learning_rate: Learning rate for training
            steps: Number of training steps
            multiresolution_training: Whether to use multiresolution training
            subject_crop: Whether to crop the subject
            
        Returns:
            The subscription result
        """
        result = await fal_client.subscribe_async(
            "fal-ai/flux-lora-portrait-trainer",
            arguments={
                "images_data_url": images_data_url,
                "learning_rate": learning_rate, 
                "steps": steps,
                "multiresolution_training": multiresolution_training,
                "subject_crop": subject_crop
            },
            with_logs=True,
            on_queue_update=self.on_queue_update,
        )
        return result



        



# Example usage
if __name__ == "__main__":
    # Create client instance
    client = FalClient()

    # Run subscribe method asynchronously and save result
    async def main():
        result = await client.subscribe(
            images_data_url="your_images_url_here",
            learning_rate=0.00009,
            steps=2500,
            multiresolution_training=True,
            subject_crop=True
        )
        print("Training completed. Result:", result)

    # Run the async function
    import asyncio
    asyncio.run(main())


