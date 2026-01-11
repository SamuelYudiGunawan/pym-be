"""
Rate Limiter using Semaphore for Concurrent Request Control
===========================================================

This module implements a rate limiter using threading.Semaphore to limit
the number of concurrent operations (e.g., database writes).

Semaphore is a synchronization primitive that maintains a counter. When
a thread wants to access a resource, it must acquire the semaphore
(decrement counter). When done, it releases the semaphore (increment counter).
If the counter reaches zero, subsequent acquire() calls will block until
a thread releases the semaphore.

This prevents too many concurrent operations from overwhelming the system,
particularly useful for database connection pools or rate-limited APIs.
"""

import threading
import time
from typing import Optional


class RateLimiter:
    """
    Rate limiter using semaphore to control concurrent access to resources.
    
    This class uses a semaphore to limit the number of concurrent operations.
    When max_concurrent operations are already running, new requests will wait
    until one completes and releases the semaphore.
    
    Attributes:
        semaphore: threading.Semaphore instance controlling concurrent access
        max_concurrent: Maximum number of concurrent operations allowed
        timeout: Maximum time to wait for semaphore acquisition (seconds)
    """
    
    def __init__(self, max_concurrent: int = 5, timeout: Optional[float] = None):
        """
        Initialize the rate limiter.
        
        Args:
            max_concurrent: Maximum number of concurrent operations allowed
            timeout: Maximum time to wait for semaphore (None = wait indefinitely)
        """
        self.semaphore = threading.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self._acquired_count = 0
        self._lock = threading.Lock()  # Protect _acquired_count
    
    def acquire(self, blocking: bool = True) -> bool:
        """
        Acquire the semaphore (decrement counter).
        
        This method attempts to acquire the semaphore. If blocking=True and
        the semaphore is at capacity, it will wait until a slot becomes available
        or timeout occurs.
        
        Args:
            blocking: If True, wait for semaphore; if False, return immediately
            
        Returns:
            True if semaphore acquired, False if timeout or non-blocking and unavailable
        """
        if blocking:
            if self.timeout:
                acquired = self.semaphore.acquire(timeout=self.timeout)
            else:
                self.semaphore.acquire()  # Wait indefinitely
                acquired = True
        else:
            acquired = self.semaphore.acquire(blocking=False)
        
        if acquired:
            with self._lock:
                self._acquired_count += 1
        
        return acquired
    
    def release(self) -> None:
        """
        Release the semaphore (increment counter).
        
        This method releases the semaphore, allowing another waiting thread
        to acquire it. Must be called after acquire() to prevent resource leaks.
        """
        with self._lock:
            if self._acquired_count > 0:
                self._acquired_count -= 1
        self.semaphore.release()
    
    def get_available_slots(self) -> int:
        """
        Get the number of available slots (approximate).
        
        Returns:
            Approximate number of available concurrent slots
        """
        # Semaphore doesn't expose internal counter, so we estimate
        # based on max_concurrent and acquired count
        with self._lock:
            return max(0, self.max_concurrent - self._acquired_count)
    
    def __enter__(self):
        """Context manager entry: acquire semaphore."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: release semaphore."""
        self.release()


# Global rate limiter instance for database operations
# Limits concurrent database write operations to prevent connection pool exhaustion
# NOTE: With multiple Gunicorn workers, each process has its own semaphore.
# With 2 workers and max_concurrent=2, total capacity = 4 concurrent operations.
# This ensures rate limiting is visible when testing with multiple workers.
db_rate_limiter = RateLimiter(max_concurrent=2, timeout=10.0)

