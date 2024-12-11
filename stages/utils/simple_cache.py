import os
import pickle
import time
import functools
from pathlib import Path
from typing import Optional, Callable, Any

def simple_cache(cache_dir: str, expiry_seconds: Optional[int] = None) -> Callable:
    """
    A decorator that caches function results to disk with optional expiry.
    
    Args:
        cache_dir: Directory to store cache files
        expiry_seconds: Optional number of seconds before cache expires
        
    Returns:
        Decorated function with caching behavior
    """
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function name and arguments
            # Use hash of args/kwargs to avoid invalid filenames
            args_str = str(hash(str(args)))
            kwargs_str = str(hash(str(kwargs)))
            cache_key = f"{func.__name__}_{args_str}_{kwargs_str}"
            cache_file = cache_path / f"{cache_key}.pkl"
            
            # Check if valid cache exists
            if cache_file.exists():
                # Check expiry if specified
                if expiry_seconds is not None:
                    modified_time = os.path.getmtime(cache_file)
                    if time.time() - modified_time > expiry_seconds:
                        cache_file.unlink()  # Delete expired cache
                    else:
                        with open(cache_file, 'rb') as f:
                            return pickle.load(f)
                else:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
            
            # Cache miss - call function and cache result
            result = func(*args, **kwargs)
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
            return result
            
        return wrapper
    return decorator
