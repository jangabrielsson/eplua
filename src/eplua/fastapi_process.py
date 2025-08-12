"""
FastAPI Server Process for EPLua
Runs FastAPI in a separate process and communicates with the main Lua engine via IPC
This eliminates asyncio event loop conflicts and provides a stable web server
"""

import json
import logging
import multiprocessing
import queue
import time
import uuid
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

logger = logging.getLogger(__name__)


class LuaExecuteRequest(BaseModel):
    """Pydantic model for POST /plua/execute"""
    code: str
    timeout: float = 30.0


class LuaExecuteResponse(BaseModel):
    """Pydantic model for execute response"""
    success: bool
    result: Any = None
    output: str = ""
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class IPCMessage(BaseModel):
    """Message format for IPC communication"""
    id: str
    type: str  # "execute", "fibaro_api", "response"
    data: Dict[str, Any]
    timestamp: float


def create_fastapi_app(request_queue: multiprocessing.Queue, response_queue: multiprocessing.Queue, config: Dict[str, Any]) -> FastAPI:
    """Create the FastAPI application with IPC communication"""
    
    app = FastAPI(
        title="EPLua API Server", 
        description="REST API for EPLua Lua Runtime with Web UI support (Multi-Process)",
        version="2.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Server statistics
    start_time = time.time()
    request_count = 0
    
    # Helper function to send IPC request and wait for response
    async def send_ipc_request(message_type: str, data: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        """Send an IPC request and wait for response"""
        nonlocal request_count
        request_count += 1
        
        message_id = str(uuid.uuid4())
        message = IPCMessage(
            id=message_id,
            type=message_type,
            data=data,
            timestamp=time.time()
        )
        
        try:
            # Send request to main process
            request_queue.put(message.dict(), timeout=1.0)
            
            # Wait for response
            start_wait = time.time()
            while time.time() - start_wait < timeout:
                try:
                    response_data = response_queue.get(timeout=0.1)
                    if response_data.get("id") == message_id:
                        return response_data.get("data", {})
                except queue.Empty:
                    continue
                    
            return {"success": False, "error": f"IPC timeout after {timeout} seconds"}
            
        except Exception as e:
            return {"success": False, "error": f"IPC error: {str(e)}"}
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        uptime = time.time() - start_time
        return {
            "status": "healthy",
            "uptime_seconds": uptime,
            "requests_served": request_count,
            "mode": "multi-process",
            "lua_engine": "connected via IPC",
            "fibaro_api": "available (hook-based)"
        }
        
    # Main page
    @app.get("/", response_class=HTMLResponse)
    async def root():
        uptime = time.time() - start_time
        status_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EPLua API Server (Multi-Process)</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ background: #e8f5e8; padding: 20px; border-radius: 5px; }}
                .info {{ margin: 10px 0; }}
                .multiprocess {{ background: #f0f8ff; border-left: 4px solid #0066cc; padding: 10px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>🚀 EPLua API Server</h1>
            <div class="multiprocess">
                <strong>🔄 Multi-Process Architecture</strong><br>
                This FastAPI server runs in a separate process from the Lua engine,
                providing maximum stability and avoiding event loop conflicts.
            </div>
            <div class="status">
                <div class="info"><strong>Status:</strong> Running</div>
                <div class="info"><strong>Uptime:</strong> {uptime:.1f} seconds</div>
                <div class="info"><strong>Requests Served:</strong> {request_count}</div>
                <div class="info"><strong>Architecture:</strong> Multi-Process</div>
                <div class="info"><strong>Lua Engine:</strong> ✅ Connected via IPC</div>
                <div class="info"><strong>Fibaro API:</strong> ✅ Available (hook-based)</div>
            </div>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/health">GET /health</a> - Health check</li>
                <li>POST /plua/execute - Execute Lua code</li>
                <li>GET/POST/PUT/DELETE /api/* - Fibaro API endpoints (if enabled)</li>
                <li><a href="/docs">GET /docs</a> - API Documentation</li>
            </ul>
        </body>
        </html>
        """
        return status_html
        
    # Lua execution endpoint
    @app.post("/plua/execute", response_model=LuaExecuteResponse)
    async def execute_lua(request: LuaExecuteRequest):
        """Execute Lua code via IPC"""
        start_time = time.time()
        
        # Send execution request via IPC
        result = await send_ipc_request(
            "execute",
            {
                "code": request.code,
                "timeout": request.timeout
            },
            timeout=request.timeout + 5.0  # Add buffer for IPC overhead
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        return LuaExecuteResponse(
            success=result.get("success", False),
            result=result.get("result"),
            output=result.get("output", ""),
            error=result.get("error"),
            execution_time_ms=execution_time
        )
    
    # Fibaro API endpoints - always available, hook determines response
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def fibaro_api(request: Request, path: str):
        """Handle Fibaro API requests via IPC - always call the hook"""
        method = request.method
        body_data = None
        
        if method in ["POST", "PUT"] and await request.body():
            try:
                body_data = await request.json()
            except Exception:
                body_data = None
                
        # Always send fibaro request via IPC - hook will handle it
        result = await send_ipc_request(
            "fibaro_api",
            {
                "method": method,
                "path": f"/api/{path}",
                "data": body_data
            },
            timeout=30.0
        )
        
        # Handle hook response
        if result.get("success", False):
            hook_result = result.get("data")
            status_code = result.get("status_code", 200)
            
            # If hook returned a non-200 status code, return error
            if status_code != 200:
                error_msg = hook_result if isinstance(hook_result, str) else f"Fibaro API unavailable"
                raise HTTPException(status_code=status_code, detail=error_msg)
                
            return hook_result
        else:
            # IPC failed
            status_code = result.get("status_code", 500)
            error_msg = result.get("error", "Fibaro API hook error")
            raise HTTPException(status_code=status_code, detail=error_msg)
    
    return app


def run_fastapi_server(request_queue: multiprocessing.Queue, response_queue: multiprocessing.Queue, config: Dict[str, Any]):
    """Run the FastAPI server in a separate process"""
    # Set up logging for the server process
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("fastapi_process")
    logger.info(f"Starting FastAPI server process on {config['host']}:{config['port']}")
    
    try:
        # Create the FastAPI app
        app = create_fastapi_app(request_queue, response_queue, config)
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host=config.get("host", "localhost"),
            port=config.get("port", 8080),
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"FastAPI server process error: {e}")
    finally:
        logger.info("FastAPI server process stopped")


class FastAPIProcessManager:
    """Manages the FastAPI server process and IPC communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8080, config: Dict[str, Any] = None):
        self.host = host
        self.port = port
        self.config = config or {}
        self.config.update({"host": host, "port": port})
        
        # IPC queues
        self.request_queue = multiprocessing.Queue()
        self.response_queue = multiprocessing.Queue()
        
        # Process management
        self.server_process: Optional[multiprocessing.Process] = None
        self.running = False
        
        # Callbacks
        self.lua_executor: Optional[callable] = None
        self.fibaro_callback: Optional[callable] = None
        
    def set_lua_executor(self, executor: callable):
        """Set the Lua code executor function"""
        self.lua_executor = executor
        logger.info("Lua executor set for FastAPI process")
        
    def set_fibaro_callback(self, callback: callable):
        """Set the Fibaro API callback function"""
        self.fibaro_callback = callback
        logger.info("Fibaro API callback set for FastAPI process")
        
    def start(self):
        """Start the FastAPI server process"""
        if self.running:
            logger.warning("FastAPI process already running")
            return
            
        logger.info(f"Starting FastAPI server process on {self.host}:{self.port}")
        
        # Start the server process
        self.server_process = multiprocessing.Process(
            target=run_fastapi_server,
            args=(self.request_queue, self.response_queue, self.config),
            daemon=True
        )
        self.server_process.start()
        self.running = True
        
        # Start IPC message handler in a thread
        import threading
        self.ipc_thread = threading.Thread(target=self._handle_ipc_messages, daemon=True)
        self.ipc_thread.start()
        
        logger.info(f"FastAPI process started with PID {self.server_process.pid}")
        
    def stop(self):
        """Stop the FastAPI server process"""
        if not self.running:
            return
            
        logger.info("Stopping FastAPI server process...")
        self.running = False
        
        if self.server_process and self.server_process.is_alive():
            self.server_process.terminate()
            self.server_process.join(timeout=5)
            
            if self.server_process.is_alive():
                logger.warning("Force killing FastAPI process")
                self.server_process.kill()
                
        logger.info("FastAPI server process stopped")
        
    def _handle_ipc_messages(self):
        """Handle IPC messages from the FastAPI process"""
        logger.info("IPC message handler started")
        
        while self.running:
            try:
                # Get message from FastAPI process
                message_data = self.request_queue.get(timeout=1.0)
                message = IPCMessage(**message_data)
                
                # Process the message
                response_data = None
                
                if message.type == "execute" and self.lua_executor:
                    # Execute Lua code
                    data = message.data
                    try:
                        result = self.lua_executor(data["code"], data.get("timeout", 30.0))
                        response_data = {"success": True, **result}
                    except Exception as e:
                        response_data = {"success": False, "error": str(e)}
                        
                elif message.type == "fibaro_api":
                    # Always handle Fibaro API call - hook will determine response
                    data = message.data
                    try:
                        if self.fibaro_callback:
                            # Call the hook function
                            hook_result, status_code = self.fibaro_callback(
                                data["method"], 
                                data["path"], 
                                json.dumps(data["data"]) if data["data"] else None
                            )
                            
                            # Handle the hook response - pass through status code
                            if status_code == 200:
                                response_data = {
                                    "success": True, 
                                    "data": hook_result,
                                    "status_code": 200
                                }
                            else:
                                # Non-200 status code - this will trigger HTTPException in FastAPI
                                response_data = {
                                    "success": True,  # IPC succeeded 
                                    "data": hook_result,
                                    "status_code": status_code
                                }
                        else:
                            # No callback set - this shouldn't happen but handle gracefully
                            response_data = {
                                "success": False, 
                                "error": "Fibaro callback not set", 
                                "status_code": 503
                            }
                    except Exception as e:
                        response_data = {"success": False, "error": str(e), "status_code": 500}
                        
                else:
                    response_data = {"success": False, "error": "Unknown message type or no handler"}
                
                # Send response back
                response = {
                    "id": message.id,
                    "type": "response",
                    "data": response_data,
                    "timestamp": time.time()
                }
                
                self.response_queue.put(response, timeout=1.0)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"IPC message handling error: {e}")
                
        logger.info("IPC message handler stopped")
        
    def is_running(self) -> bool:
        """Check if the FastAPI process is running"""
        return self.running and self.server_process and self.server_process.is_alive()


# Global process manager instance
_process_manager: Optional[FastAPIProcessManager] = None


def get_process_manager() -> Optional[FastAPIProcessManager]:
    """Get the global process manager instance"""
    return _process_manager


def start_fastapi_process(host: str = "localhost", port: int = 8080, config: Dict[str, Any] = None) -> FastAPIProcessManager:
    """Start the global FastAPI server process"""
    global _process_manager
    
    if _process_manager and _process_manager.is_running():
        logger.warning("FastAPI process already running")
        return _process_manager
        
    _process_manager = FastAPIProcessManager(host, port, config)
    _process_manager.start()
    return _process_manager


def stop_fastapi_process():
    """Stop the global FastAPI server process"""
    global _process_manager
    
    if _process_manager:
        _process_manager.stop()
        _process_manager = None
