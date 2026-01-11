"""
Request Counter with Mutex for Thread-Safe Counting
====================================================

This module implements a thread-safe request counter using threading.Lock (mutex)
to prevent race conditions when multiple threads try to increment the counter
simultaneously.

Mutex (Mutual Exclusion) ensures that only one thread can execute a critical
section of code at a time. Without mutex protection, concurrent increments
could result in lost updates due to race conditions.

Example race condition without mutex:
  Thread 1: Read count (value=5)
  Thread 2: Read count (value=5)
  Thread 1: Increment and write (value=6)
  Thread 2: Increment and write (value=6)  # Lost update! Should be 7

With mutex:
  Thread 1: Acquire lock, read (5), increment, write (6), release lock
  Thread 2: Wait for lock, acquire lock, read (6), increment, write (7), release lock
"""

import threading
from collections import defaultdict
from typing import Dict


class RequestCounter:
    """
    Thread-safe request counter using mutex (threading.Lock).
    
    This class tracks request counts in a thread-safe manner, preventing
    race conditions when multiple threads try to increment counters
    simultaneously.
    
    Attributes:
        _total_count: Total number of requests
        _endpoint_counts: Dictionary mapping endpoint paths to request counts
        _lock: threading.Lock (mutex) protecting shared state
    """
    
    def __init__(self):
        """Initialize the request counter with zero counts."""
        self._total_count = 0
        self._endpoint_counts = defaultdict(int)
        self._lock = threading.Lock()  # Mutex for thread safety
    
    def increment(self, endpoint: str = "unknown") -> int:
        """
        Increment the total counter and endpoint-specific counter.
        
        This method is thread-safe. The mutex ensures that only one thread
        can modify the counters at a time, preventing race conditions.
        
        Args:
            endpoint: The endpoint path (e.g., '/api/notes/')
            
        Returns:
            The new total count after increment
        """
        with self._lock:  # Acquire mutex (blocks other threads)
            self._total_count += 1
            self._endpoint_counts[endpoint] += 1
            return self._total_count
        # Mutex automatically released when exiting 'with' block
    
    def get_total_count(self) -> int:
        """
        Get the total request count (thread-safe).
        
        Returns:
            Total number of requests processed
        """
        with self._lock:
            return self._total_count
    
    def get_endpoint_counts(self) -> Dict[str, int]:
        """
        Get request counts per endpoint (thread-safe).
        
        Returns:
            Dictionary mapping endpoint paths to request counts
        """
        with self._lock:
            # Return a copy to prevent external modification
            return dict(self._endpoint_counts)
    
    def get_count_for_endpoint(self, endpoint: str) -> int:
        """
        Get request count for a specific endpoint (thread-safe).
        
        Args:
            endpoint: The endpoint path
            
        Returns:
            Number of requests for this endpoint
        """
        with self._lock:
            return self._endpoint_counts.get(endpoint, 0)
    
    def reset(self) -> None:
        """
        Reset all counters to zero (thread-safe).
        
        Useful for testing or periodic resets.
        """
        with self._lock:
            self._total_count = 0
            self._endpoint_counts.clear()
    
    def get_stats(self) -> Dict:
        """
        Get comprehensive statistics (thread-safe).
        
        Returns:
            Dictionary containing total count and per-endpoint counts
        """
        with self._lock:
            return {
                'total_requests': self._total_count,
                'endpoint_counts': dict(self._endpoint_counts),
                'unique_endpoints': len(self._endpoint_counts)
            }


# Global request counter instance
# This is shared across all threads and processes (within same process)
request_counter = RequestCounter()

