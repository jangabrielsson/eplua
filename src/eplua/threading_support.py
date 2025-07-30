"""
Threading support for EPLua - demonstrates cross-thread callback communication.

This module shows how to execute Python functions in separate threads and
communicate results back to the main Lua event loop via callbacks.
"""

import threading
import time
import logging
from .lua_bindings import export_to_lua, get_global_engine

logger = logging.getLogger(__name__)


@export_to_lua("run_in_thread")
def run_in_thread(callback_id: int, delay_seconds: float = 1.0) -> None:
    """
    Example function that runs in a separate thread and posts result back.
    
    Args:
        callback_id: The callback ID from _PY.registerCallback()
        delay_seconds: How long to simulate work (default 1.0 seconds)
    """
    def worker():
        try:
            logger.info(f"Thread worker starting with {delay_seconds}s delay")
            
            # Simulate some work (could be file I/O, network, CPU-intensive task, etc.)
            time.sleep(delay_seconds)
            
            # Simulate different results
            if delay_seconds > 2.0:
                # Simulate an error
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(
                        callback_id, 
                        error="Task took too long!"
                    )
            else:
                # Success case
                result = {
                    'success': True,
                    'delay': delay_seconds,
                    'thread_id': threading.get_ident(),
                    'message': f'Task completed after {delay_seconds} seconds'
                }
                
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, error=None, result=result)
                
        except Exception as e:
            # Handle any unexpected errors
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, error=str(e))
    
    # Start the worker in a separate thread
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


@export_to_lua("cpu_intensive_task")
def cpu_intensive_task(callback_id: int, iterations: int = 1000000) -> None:
    """
    Example CPU-intensive task that runs in a separate thread.
    
    Args:
        callback_id: The callback ID from _PY.registerCallback()
        iterations: Number of iterations to perform
    """
    def worker():
        try:
            logger.info(f"Starting CPU-intensive task with {iterations} iterations")
            
            # Simulate CPU-intensive work
            total = 0
            for i in range(iterations):
                total += i * i
            
            result = {
                'success': True,
                'iterations': iterations,
                'result': total,
                'thread_id': threading.get_ident()
            }
            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, error=None, result=result)
                
        except Exception as e:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, error=str(e))
    
    # Start the worker in a separate thread
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


@export_to_lua("file_operation")
def file_operation(callback_id: int, file_path: str, operation: str = "read") -> None:
    """
    Example file operation that runs in a separate thread.
    
    Args:
        callback_id: The callback ID from _PY.registerCallback()
        file_path: Path to the file
        operation: "read" or "write"
    """
    def worker():
        try:
            if operation == "read":
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    result = {
                        'success': True,
                        'operation': 'read',
                        'file_path': file_path,
                        'content_length': len(content),
                        'content': content[:100] + '...' if len(content) > 100 else content
                    }
                except FileNotFoundError:
                    engine = get_global_engine()
                    if engine:
                        engine.post_callback_from_thread(callback_id, error=f"File not found: {file_path}")
                    return
                    
            elif operation == "write":
                test_content = f"Test file written from thread {threading.get_ident()}"
                with open(file_path, 'w') as f:
                    f.write(test_content)
                
                result = {
                    'success': True,
                    'operation': 'write',
                    'file_path': file_path,
                    'bytes_written': len(test_content)
                }
            else:
                engine = get_global_engine()
                if engine:
                    engine.post_callback_from_thread(callback_id, error=f"Unknown operation: {operation}")
                return
            
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, error=None, result=result)
                
        except Exception as e:
            engine = get_global_engine()
            if engine:
                engine.post_callback_from_thread(callback_id, error=str(e))
    
    # Start the worker in a separate thread
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
