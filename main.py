from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import uvicorn

from config import config
from ai_parser import AIParser
from automation_engine import AutomationEngine
from task_manager import TaskManager

# Initialize FastAPI
app = FastAPI(title="System Automation Controller")

# Initialize components
ai_parser = AIParser(use_local_llm=config.USE_LOCAL_LLM)
automation_engine = AutomationEngine()
task_manager = TaskManager()

# WebSocket connections
active_connections: List[WebSocket] = []

# Models
class CommandRequest(BaseModel):
    command: str
    require_confirmation: bool = True

class CommandResponse(BaseModel):
    task_id: str
    parsed_actions: List[Dict[str, Any]]
    status: str

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend."""
    return get_frontend_html()

@app.post("/api/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Parse and execute command."""
    try:
        # Parse command
        actions = ai_parser.parse_command(request.command)
        
        if not actions:
            raise HTTPException(status_code=400, detail="Could not parse command")
        
        # Create task
        task = task_manager.create_task(request.command, actions)
        
        # Add to queue
        await task_manager.add_task(task)
        
        # Broadcast to WebSocket clients
        await broadcast_message({
            "type": "new_task",
            "task_id": task.id,
            "command": request.command,
            "actions": actions
        })
        
        return CommandResponse(
            task_id=task.id,
            parsed_actions=actions,
            status="queued"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_tasks():
    """Get all tasks."""
    return JSONResponse(content=task_manager.get_all_tasks())

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and result."""
    result = task_manager.get_task_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content=result)

@app.post("/api/parse")
async def parse_command(request: CommandRequest):
    """Parse command without executing."""
    try:
        actions = ai_parser.parse_command(request.command)
        return JSONResponse(content={"actions": actions})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_message(message: dict):
    """Broadcast message to all WebSocket clients."""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass

@app.on_event("startup")
async def startup_event():
    """Start background task processor."""
    asyncio.create_task(task_manager.process_queue(automation_engine))

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    task_manager.stop_processing()
    automation_engine.cleanup()

def get_frontend_html() -> str:
    """Return frontend HTML."""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Automation Controller</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 30px; }
        .input-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .input-group { margin-bottom: 20px; }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            min-height: 100px;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .examples {
            background: #fff3cd;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .examples h3 {
            color: #856404;
            margin-bottom: 15px;
        }
        .example-item {
            background: white;
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .example-item:hover {
            background: #ffeaa7;
        }
        .status {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .tasks-section { margin-top: 30px; }
        .task-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .task-command {
            font-weight: 600;
            font-size: 1.1em;
            color: #333;
        }
        .task-status {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }
        .status-pending { background: #ffeaa7; color: #d63031; }
        .status-running { background: #74b9ff; color: #0984e3; }
        .status-completed { background: #55efc4; color: #00b894; }
        .status-failed { background: #ff7675; color: #d63031; }
        .action-list {
            margin-top: 15px;
            padding-left: 20px;
        }
        .action-item {
            padding: 8px;
            margin: 5px 0;
            background: white;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI System Automation Controller</h1>
            <p>Control your computer with natural language commands</p>
        </div>
        
        <div class="content">
            <div class="examples">
                <h3>📋 Example Commands (Click to use):</h3>
                <div class="example-item" onclick="setCommand('open chrome, search youtube, play relaxing music')">
                    🎵 Open Chrome, search YouTube, play relaxing music
                </div>
                <div class="example-item" onclick="setCommand('open notepad and type Hello World')">
                    📝 Open Notepad and type "Hello World"
                </div>
                <div class="example-item" onclick="setCommand('search google for weather today')">
                    🌤️ Search Google for weather today
                </div>
                <div class="example-item" onclick="setCommand('open calculator')">
                    🔢 Open Calculator
                </div>
            </div>
            
            <div class="input-section">
                <div class="input-group">
                    <label for="commandInput">Enter Your Command:</label>
                    <textarea 
                        id="commandInput" 
                        placeholder="Example: open chrome, search youtube for songs, play first video"
                    ></textarea>
                </div>
                <button class="btn" id="executeBtn" onclick="executeCommand()">
                    🚀 Execute Command
                </button>
            </div>
            
            <div id="statusMessage" class="status"></div>
            
            <div class="tasks-section">
                <h2>Recent Tasks</h2>
                <div id="tasksList"></div>
            </div>
        </div>
    </div>

    <script>
        const API_URL = window.location.origin;
        let ws;
        
        // Connect WebSocket
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'new_task') {
                    loadTasks();
                }
            };
            
            ws.onclose = () => {
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        connectWebSocket();
        
        function setCommand(cmd) {
            document.getElementById('commandInput').value = cmd;
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('statusMessage');
            status.textContent = message;
            status.className = `status ${type}`;
            status.style.display = 'block';
            
            setTimeout(() => {
                status.style.display = 'none';
            }, 5000);
        }
        
        async function executeCommand() {
            const command = document.getElementById('commandInput').value.trim();
            
            if (!command) {
                showStatus('Please enter a command', 'error');
                return;
            }
            
            const btn = document.getElementById('executeBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> Executing...';
            
            try {
                const response = await fetch(`${API_URL}/api/execute`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command, require_confirmation: false })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showStatus(`✅ Task queued successfully! Task ID: ${data.task_id}`, 'success');
                    loadTasks();
                    monitorTask(data.task_id);
                } else {
                    showStatus(`❌ Error: ${data.detail}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Error: ${error.message}`, 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '🚀 Execute Command';
            }
        }
        
        async function loadTasks() {
            try {
                const response = await fetch(`${API_URL}/api/tasks`);
                const tasks = await response.json();
                
                const tasksList = document.getElementById('tasksList');
                
                if (tasks.length === 0) {
                    tasksList.innerHTML = '<p>No tasks yet. Execute a command to get started!</p>';
                    return;
                }
                
                tasksList.innerHTML = tasks.slice(-5).reverse().map(task => `
                    <div class="task-card">
                        <div class="task-header">
                            <div class="task-command">${task.command}</div>
                            <div class="task-status status-${task.status}">${task.status.toUpperCase()}</div>
                        </div>
                        <small>Started: ${new Date(task.created_at).toLocaleString()}</small>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading tasks:', error);
            }
        }
        
        async function monitorTask(taskId) {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(`${API_URL}/api/tasks/${taskId}`);
                    const task = await response.json();
                    
                    if (task.status === 'completed' || task.status === 'failed') {
                        clearInterval(interval);
                        loadTasks();
                        
                        if (task.status === 'completed') {
                            showStatus('✅ Task completed successfully!', 'success');
                        } else {
                            showStatus('❌ Task failed: ' + (task.error || 'Unknown error'), 'error');
                        }
                    }
                } catch (error) {
                    clearInterval(interval);
                }
            }, 2000);
        }
        
        // Load initial tasks
        loadTasks();
        
        // Enter key to execute
        document.getElementById('commandInput').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                executeCommand();
            }
        });
    </script>
</body>
</html>
    '''

# Run server
if __name__ == "__main__":
    print("🚀 Starting System Automation Controller...")
    print(f"📡 Server running at http://{config.HOST}:{config.PORT}")
    print(f"🤖 Using {'Local LLM (Ollama)' if config.USE_LOCAL_LLM else 'OpenAI API'}")
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level="info"
    )
