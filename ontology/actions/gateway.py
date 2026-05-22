import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ActionGateway:
    """
    Translates abstract CDFD Rule Actions into real-world physical Webhooks/APIs.
    This is the core of the 'Palantir-Killer' - the ability to writeback and alter reality.
    """
    def __init__(self):
        self.registered_webhooks = {}
        
    def register_webhook(self, action_name: str, url: str, method: str = "POST", headers: Optional[Dict] = None):
        """
        Binds a semantic action (e.g., 'reduce_flux') to an external API endpoint.
        """
        self.registered_webhooks[action_name] = {
            "url": url,
            "method": method.upper(),
            "headers": headers or {}
        }
        logger.info(f"Registered Webhook for action '{action_name}' -> {url}")

    def execute_action(self, action_name: str, system_name: str, psi_val: float) -> Dict[str, Any]:
        """
        Triggered by the DSL RuleNode when a threshold is breached.
        """
        result = {
            "action": action_name,
            "system": system_name,
            "psi": psi_val,
            "status": "dry_run",
            "message": "Action logged successfully."
        }
        
        if action_name in self.registered_webhooks:
            hook = self.registered_webhooks[action_name]
            payload = {
                "triggered_by_system": system_name,
                "current_psi": psi_val,
                "recommendation": f"Action '{action_name}' mandated by CDFD Runtime."
            }
            try:
                if hook["method"] == "POST":
                    resp = requests.post(hook["url"], json=payload, headers=hook["headers"], timeout=5)
                    result["status"] = "executed"
                    result["http_code"] = resp.status_code
                elif hook["method"] == "GET":
                    resp = requests.get(hook["url"], params=payload, headers=hook["headers"], timeout=5)
                    result["status"] = "executed"
                    result["http_code"] = resp.status_code
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                logger.error(f"Failed to execute webhook for {action_name}: {e}")
        
        return result
