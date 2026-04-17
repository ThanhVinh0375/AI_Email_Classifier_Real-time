"""Utility decorators"""
import functools
import asyncio
from typing import Callable, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Max retries exceeded for {func.__name__}: {str(e)}")
                        raise
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} "
                        f"after {current_delay}s: {str(e)}"
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Max retries exceeded for {func.__name__}: {str(e)}")
                        raise
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} "
                        f"after {current_delay}s: {str(e)}"
                    )
                    asyncio.run(asyncio.sleep(current_delay))
                    current_delay *= backoff
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator

def log_execution(func: Callable) -> Callable:
    """Log function execution time"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        import time
        start = time.time()
        logger.info(f"Starting {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"Completed {func.__name__} in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"Failed {func.__name__} after {elapsed:.2f}s: {str(e)}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        import time
        start = time.time()
        logger.info(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"Completed {func.__name__} in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"Failed {func.__name__} after {elapsed:.2f}s: {str(e)}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
