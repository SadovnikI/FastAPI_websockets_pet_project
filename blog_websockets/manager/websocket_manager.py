from collections import defaultdict
import asyncio

class WebsocketManager:

    active_connections = defaultdict(lambda: [], {})

    async def update_connection(self, websocket, token):
        await websocket.accept()
        self.active_connections[token].append(websocket)

    def remove_connections(self, websocket, token):
        websocket_list = self.active_connections[token]
        if websocket in websocket_list:
            websocket_list.remove(websocket)

    async def broadcast(self, json_data, token):
        update_connections = []
        websocket_list = self.active_connections[token]
        for websocket in websocket_list:
            await websocket.send_json(json_data)
            update_connections.append(websocket)
        self.active_connections[token] = update_connections


websocket_manager = WebsocketManager()
