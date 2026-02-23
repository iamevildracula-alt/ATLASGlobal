import asyncio
import json
from typing import Set, Dict, Any, Optional

class TelemetryBroadcaster:
    def __init__(self):
        self.subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    async def broadcast(self, data: Dict[str, Any]):
        if not self.subscribers:
            return

        # Prepare payload once
        payload = json.dumps(data)
        
        # Dispatch to all queues
        tasks = [queue.put(payload) for queue in self.subscribers]
        await asyncio.gather(*tasks)

# Global broadcaster instance
broadcaster = TelemetryBroadcaster()
