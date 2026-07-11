"""EventBus using asyncio pub/sub with optional ZeroMQ transport."""

from __future__ import annotations

import asyncio
import json
import platform
import threading
from collections.abc import Callable

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class EventBus:
    def __init__(self, bind_addr: str, connect_addr: str) -> None:
        self._bind_addr = bind_addr
        self._connect_addr = connect_addr
        self._subscribers: dict[str, list[Callable]] = {}
        self._lock = threading.Lock()
        self._running = False
        self._use_zmq = bind_addr.startswith("tcp://") or bind_addr.startswith("ipc://")
        if self._use_zmq:
            import zmq
            import zmq.asyncio
            self._zmq = zmq
            self._ctx = zmq.asyncio.Context()
            self._pub: zmq.asyncio.Socket | None = None
            self._sub: zmq.asyncio.Socket | None = None
        else:
            self._queue: asyncio.Queue = asyncio.Queue()

    async def start(self) -> None:
        self._running = True
        if self._use_zmq:
            self._pub = self._ctx.socket(self._zmq.PUB)
            self._pub.bind(self._bind_addr)
            self._sub = self._ctx.socket(self._zmq.SUB)
            self._sub.connect(self._connect_addr)
            self._sub.setsockopt_string(self._zmq.SUBSCRIBE, "")
            asyncio.create_task(self._listen_zmq())
        else:
            asyncio.create_task(self._listen_local())

    async def _listen_local(self) -> None:
        while self._running:
            try:
                topic, payload = await asyncio.wait_for(self._queue.get(), timeout=0.5)
                for cb in self._subscribers.get(topic, []):
                    try:
                        data = json.loads(payload)
                        if asyncio.iscoroutinefunction(cb):
                            await cb(data)
                        else:
                            cb(data)
                    except Exception:
                        pass
            except TimeoutError:
                continue

    async def _listen_zmq(self) -> None:
        while self._running and self._sub is not None:
            try:
                msg = await asyncio.wait_for(self._sub.recv_string(), timeout=0.5)
                topic, _, payload = msg.partition(" ")
                for cb in self._subscribers.get(topic, []):
                    try:
                        data = json.loads(payload)
                        if asyncio.iscoroutinefunction(cb):
                            await cb(data)
                        else:
                            cb(data)
                    except Exception:
                        pass
            except self._zmq.ZMQError:
                if not self._running:
                    break

    def subscribe(self, topic: str, callback: Callable) -> None:
        with self._lock:
            self._subscribers.setdefault(topic, []).append(callback)

    async def publish(self, topic: str, payload: dict) -> None:
        if self._use_zmq:
            if self._pub is None:
                raise RuntimeError("EventBus not started")
            self._pub.send_string(f"{topic} {json.dumps(payload)}")
        else:
            await self._queue.put((topic, json.dumps(payload)))

    async def stop(self) -> None:
        self._running = False
        if self._use_zmq:
            if self._pub:
                self._pub.close()
            if self._sub:
                self._sub.close()
            self._ctx.term()
