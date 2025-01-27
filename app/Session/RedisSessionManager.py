import redis
import json
import uuid

class SessionManager:
    def __init__(self, redis_host='localhost', redis_port=6379, session_ttl=3600):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.session_ttl = session_ttl  

    def generate_session_id(self):
        """Generate a unique session ID."""
        return str(uuid.uuid4())

    def create_session(self, session_data):
        """Create a new session and store it in Redis."""
        session_id = self.generate_session_id()
        redis_key = f"session:{session_id}"
        self.redis_client.set(redis_key, json.dumps(session_data))
        self.redis_client.expire(redis_key, self.session_ttl)
        return session_id

    def get_session(self, session_id):
        """Retrieve session data using the session ID."""
        redis_key = f"session:{session_id}"
        session_data = self.redis_client.get(redis_key)
        if session_data:
            return json.loads(session_data)
        return None

    def delete_session(self, session_id):
        """Delete a session."""
        redis_key = f"session:{session_id}"
        self.redis_client.delete(redis_key)

    def get_all_sessions(self):
        """Fetch all active sessions."""
        session_keys = self.redis_client.scan_iter("session:*")
        sessions = {}
        for key in session_keys:
            session_id = key.split(":")[1]
            session_data = self.redis_client.get(key)
            if session_data:
                sessions[session_id] = json.loads(session_data)
        return sessions
