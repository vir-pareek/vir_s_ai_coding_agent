import time
import functools
import threading
from google.api_core import exceptions
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Global timeout for API calls (in seconds)
API_CALL_TIMEOUT = 120  # 2 minutes default

# Rate limiting: track last API call time
_last_api_call_time = 0
_api_call_lock = threading.Lock()
_min_api_call_interval = 0.1  # Minimum 100ms between API calls (10 calls/second max)

class TimeoutError(Exception):
    """Custom timeout error for API calls."""
    pass

def retry_with_backoff(max_retries=5, initial_delay=2, backoff_factor=2, timeout=API_CALL_TIMEOUT):
    """
    Decorator to retry a function call with exponential backoff upon encountering
    ResourceExhausted (429) errors from the Google Gemini API.
    
    Args:
        max_retries (int): Maximum number of retries before giving up.
        initial_delay (int): Initial delay in seconds before the first retry.
        backoff_factor (int): Factor by which the delay increases after each failure.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global _last_api_call_time
            
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Rate limiting: ensure minimum interval between API calls
                    with _api_call_lock:
                        current_time = time.time()
                        time_since_last_call = current_time - _last_api_call_time
                        if time_since_last_call < _min_api_call_interval:
                            time.sleep(_min_api_call_interval - time_since_last_call)
                        _last_api_call_time = time.time()
                    
                    # Execute with timeout using ThreadPoolExecutor
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(func, *args, **kwargs)
                        try:
                            result = future.result(timeout=timeout)
                            return result
                        except FutureTimeoutError:
                            raise TimeoutError(f"API call timed out after {timeout} seconds")
                except TimeoutError as e:
                    last_exception = e
                    if attempt == max_retries:
                        print(f"❌ API Timeout: Failed after {max_retries} retries.")
                        raise last_exception
                    print(f"⚠️ API Timeout. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= backoff_factor
                except exceptions.ResourceExhausted as e:
                    last_exception = e
                    # Check if it's a "limit: 0" error which implies model unavailability
                    if "limit: 0" in str(e) or "limit:0" in str(e):
                        print(f"❌ API Error: Model quota exhausted. Consider switching to gemini-2.5-flash which has 250 free requests/day.")
                        # Don't raise immediately - let retry logic handle it
                        if attempt == max_retries:
                            raise e
                        
                    if attempt == max_retries:
                        print(f"❌ API Quota Exceeded: Failed after {max_retries} retries.")
                        raise last_exception
                    
                    print(f"⚠️ API Quota Exceeded. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= backoff_factor
                except Exception as e:
                    # Check for 429 in string representation if it's not a specific ResourceExhausted exception
                    if "429" in str(e) or "Resource has been exhausted" in str(e):
                        last_exception = e
                        if attempt == max_retries:
                            print(f"❌ API Quota Exceeded: Failed after {max_retries} retries.")
                            raise last_exception
                        
                        print(f"⚠️ API Quota Exceeded. Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        # Re-raise other exceptions immediately
                        raise e
            
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator
