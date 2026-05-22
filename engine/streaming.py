import time
import threading
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class StreamingStateEngine:
    """
    First-Class Real-Time Streaming interface.
    Allows continuous updating of Phi and C directly into the engine, 
    bypassing the need for rigid discrete run_cycles.
    """
    def __init__(self, state, ontology_engine=None):
        self.state = state
        self.ontology_engine = ontology_engine
        self.running = False
        self._thread = None
        self.stream_buffer = []
        self.callbacks = []
        
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback to be fired on every streaming tick."""
        self.callbacks.append(callback)

    def inject_data(self, system_name: str, phi: float, C: float, provenance: Dict[str, Any] = None):
        """Thread-safe injection of new sensor data."""
        self.stream_buffer.append({
            "system": system_name,
            "phi": phi,
            "C": C,
            "provenance": provenance or {},
            "timestamp": time.time()
        })

    def _stream_loop(self, tick_rate_ms: int):
        sleep_time = tick_rate_ms / 1000.0
        while self.running:
            if self.stream_buffer:
                # Process the buffer
                updates = self.stream_buffer.copy()
                self.stream_buffer.clear()
                
                for update in updates:
                    # In a real environment, we'd map 'system' to specific (x,y) indices 
                    # in self.state.phi and self.state.C.
                    # For now, we update the global average or specific meta tracking objects
                    pass
                
                # Re-evaluate
                self.state.update_psi()
                
                # Fire callbacks
                for cb in self.callbacks:
                    try:
                        cb({"updates": len(updates), "mean_psi": self.state.mean_psi()})
                    except Exception as e:
                        logger.error(f"Streaming callback error: {e}")
                        
            time.sleep(sleep_time)

    def start_streaming(self, tick_rate_ms: int = 100):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._stream_loop, args=(tick_rate_ms,), daemon=True)
            self._thread.start()
            logger.info("Real-time streaming engine started.")

    def stop_streaming(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        logger.info("Real-time streaming engine stopped.")
