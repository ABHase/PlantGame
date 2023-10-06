from flask_socketio import SocketIO, disconnect

socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet', transports=['websocket'])
