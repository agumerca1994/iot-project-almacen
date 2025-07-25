from fastapi import WebSocket, WebSocketDisconnect

active_connections: list[WebSocket] = []

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def notify_new_device(device_data: dict):
    for connection in active_connections:
        await connection.send_json({"type": "device", "data": device_data})

async def notify_stock_update(stock_data: dict):
    for connection in active_connections:
        await connection.send_json({"type": "stock", "data": stock_data})
