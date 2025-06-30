import asyncio
from ._async_client import AsyncCloudClient  # Assuming _async_client.py is in the same directory
import logging

class SyncCloudClient:
    """
    A synchronous wrapper for the AsyncCloudClient.

    This client provides a blocking interface to the cloud services,
    making it easier to use in synchronous Python applications.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the synchronous client.
        It creates an instance of the asynchronous client internally.
        """
        self._async_client = AsyncCloudClient(*args, **kwargs)
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        logging.debug("SyncCloudClient initialized.")

    def _run_async(self, coro):
        """
        Helper method to run an async coroutine synchronously.
        """
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # If called from within an already running asyncio event loop,
                # it's tricky to directly run another coroutine to completion
                # without blocking. This is a common issue with bridging sync/async.
                # For simplicity here, we'll raise an error or handle as needed.
                # A more robust solution might involve creating a separate thread
                # to run the async code.
                # This part might need more sophisticated handling depending on the exact usage context.
                # For now, let's assume this will work in most common scenarios or
                # the user is aware they shouldn't call sync from async directly.
                if loop is not self._loop and self._loop.is_running():
                    logging.warning("Running synchronous method from a different event loop. This might cause issues.")
                return loop.run_until_complete(coro)
            else:
                # If get_running_loop() returned a loop but it's not running,
                # we can use it.
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop is currently running, so asyncio.run will create one.
            return asyncio.run(coro)

    # --- Mirrored methods from AsyncCloudClient ---
    # Replace these example methods with the actual methods from your AsyncCloudClient

    def get_item(self, item_id: str):
        """
        Synchronous wrapper for the async get_item method.
        """
        logging.debug(f"Sync: Calling get_item for ID: {item_id}")
        return self._run_async(self._async_client.get_item(item_id))

    def create_item(self, item_data: dict):
        """
        Synchronous wrapper for the async create_item method.
        """
        logging.debug(f"Sync: Calling create_item with data: {item_data}")
        return self._run_async(self._async_client.create_item(item_data))

    def update_item(self, item_id: str, item_data: dict):
        """
        Synchronous wrapper for the async update_item method.
        """
        logging.debug(f"Sync: Calling update_item for ID: {item_id} with data: {item_data}")
        return self._run_async(self._async_client.update_item(item_id, item_data))

    def delete_item(self, item_id: str):
        """
        Synchronous wrapper for the async delete_item method.
        """
        logging.debug(f"Sync: Calling delete_item for ID: {item_id}")
        return self._run_async(self._async_client.delete_item(item_id))

    # -----------------------------------------------------------------

    def close(self):
        """
        Closes any underlying resources, such as the HTTP client session
        used by the async client.
        """
        if hasattr(self._async_client, 'close') and callable(getattr(self._async_client, 'close')):
            logging.debug("Closing underlying async client resources.")
            try:
                if asyncio.iscoroutinefunction(self._async_client.close):
                    if self._loop.is_running():
                        asyncio.ensure_future(self._async_client.close(), loop=self._loop)
                    else:
                        self._loop.run_until_complete(self._async_client.close())
                else:
                    self._async_client.close()
            except Exception as e:
                logging.error(f"Error during SyncCloudClient close: {e}", exc_info=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Example usage (for testing this file directly, not part of the library):
if __name__ == '__main__':
    # This is just for demonstration and won't run without a real AsyncCloudClient
    # and proper configuration.
    print("SyncCloudClient class defined. To use, import and instantiate it in your application.")
    # Example (assuming AsyncCloudClient and config.json are set up):
    # try:
    #     client = SyncCloudClient(api_key="YOUR_API_KEY", base_url="YOUR_API_URL")
    #     # item = client.get_item("some_item_id")
    #     # print(f"Fetched item: {item}")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    # finally:
    #     if 'client' in locals() and client:
    #         client.close()
