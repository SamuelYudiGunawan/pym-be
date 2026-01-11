"""
Synchronization Demonstration: Race Condition Example
======================================================

This module demonstrates the importance of synchronization mechanisms
by showing what happens with and without mutex protection.

It implements two counters:
1. UnsafeCounter: No mutex protection - demonstrates race conditions
2. SafeCounter: With mutex protection - demonstrates correct behavior

When multiple threads increment the unsafe counter simultaneously,
race conditions occur, resulting in lost updates and incorrect final values.
The safe counter uses a mutex to prevent these issues.
"""

import threading
import time
from typing import List


class UnsafeCounter:
    """
    Counter WITHOUT mutex protection - demonstrates race conditions.
    
    This counter is NOT thread-safe. When multiple threads increment
    it simultaneously, race conditions occur:
    
    1. Thread A reads value (e.g., 5)
    2. Thread B reads value (e.g., 5)  # Before A writes
    3. Thread A increments and writes (6)
    4. Thread B increments and writes (6)  # Lost update! Should be 7
    
    Result: Final count is less than expected.
    """
    
    def __init__(self):
        """Initialize counter to zero."""
        self._count = 0
    
    def increment(self, times: int = 1) -> None:
        """
        Increment counter (NOT thread-safe).
        
        Args:
            times: Number of times to increment
        """
        for _ in range(times):
            # Simulate read-modify-write operation
            current = self._count  # Read
            time.sleep(0.0001)  # Simulate processing time (increases race condition probability)
            self._count = current + 1  # Write
    
    def get_count(self) -> int:
        """Get current count."""
        return self._count
    
    def reset(self) -> None:
        """Reset counter to zero."""
        self._count = 0


class SafeCounter:
    """
    Counter WITH mutex protection - demonstrates correct behavior.
    
    This counter is thread-safe. The mutex ensures that only one thread
    can execute the increment operation at a time, preventing race conditions.
    
    Even with multiple threads incrementing simultaneously, the final
    count will be correct.
    """
    
    def __init__(self):
        """Initialize counter to zero with mutex."""
        self._count = 0
        self._lock = threading.Lock()  # Mutex for thread safety
    
    def increment(self, times: int = 1) -> None:
        """
        Increment counter (thread-safe).
        
        Args:
            times: Number of times to increment
        """
        for _ in range(times):
            with self._lock:  # Acquire mutex
                # Critical section: only one thread can execute this at a time
                current = self._count
                time.sleep(0.0001)  # Simulate processing time
                self._count = current + 1
            # Mutex automatically released
    
    def get_count(self) -> int:
        """Get current count (thread-safe)."""
        with self._lock:
            return self._count
    
    def reset(self) -> None:
        """Reset counter to zero (thread-safe)."""
        with self._lock:
            self._count = 0


def run_concurrent_increment_test(counter, num_threads: int = 10, increments_per_thread: int = 100) -> dict:
    """
    Run concurrent increment test on a counter.
    
    This function spawns multiple threads that each increment the counter
    multiple times. The result shows whether the counter is thread-safe.
    
    Args:
        counter: Counter instance (SafeCounter or UnsafeCounter)
        num_threads: Number of concurrent threads
        increments_per_thread: Number of increments per thread
        
    Returns:
        Dictionary with test results
    """
    counter.reset()
    threads = []
    start_time = time.time()
    
    def increment_worker():
        """Worker function that increments counter."""
        counter.increment(increments_per_thread)
    
    # Create and start threads
    for _ in range(num_threads):
        thread = threading.Thread(target=increment_worker)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    elapsed = end_time - start_time
    final_count = counter.get_count()
    expected_count = num_threads * increments_per_thread
    
    return {
        'final_count': final_count,
        'expected_count': expected_count,
        'difference': expected_count - final_count,
        'accuracy_percent': (final_count / expected_count * 100) if expected_count > 0 else 0,
        'elapsed_time': elapsed,
        'lost_updates': expected_count - final_count
    }


# Global instances for demonstration
unsafe_counter = UnsafeCounter()
safe_counter = SafeCounter()


def demonstrate_race_condition() -> dict:
    """
    Demonstrate race condition by running concurrent increments on both counters.
    
    Returns:
        Dictionary comparing unsafe vs safe counter results
    """
    num_threads = 10
    increments_per_thread = 100
    
    # Test unsafe counter (will show race conditions)
    unsafe_result = run_concurrent_increment_test(
        unsafe_counter, 
        num_threads=num_threads, 
        increments_per_thread=increments_per_thread
    )
    
    # Test safe counter (will show correct behavior)
    safe_result = run_concurrent_increment_test(
        safe_counter,
        num_threads=num_threads,
        increments_per_thread=increments_per_thread
    )
    
    return {
        'unsafe_counter': unsafe_result,
        'safe_counter': safe_result,
        'demonstration': {
            'num_threads': num_threads,
            'increments_per_thread': increments_per_thread,
            'expected_total': num_threads * increments_per_thread,
            'unsafe_lost_updates': unsafe_result['lost_updates'],
            'safe_lost_updates': safe_result['lost_updates'],
            'conclusion': (
                f"Unsafe counter lost {unsafe_result['lost_updates']} updates due to race conditions. "
                f"Safe counter with mutex lost {safe_result['lost_updates']} updates (correct behavior)."
            )
        }
    }

