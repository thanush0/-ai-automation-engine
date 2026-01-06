from browser_controller import BrowserController
from system_controller import SystemController
from typing import Dict, Any, List
import time

class AutomationEngine:
    def __init__(self):
        self.browser = BrowserController()
        self.system = SystemController()
        self.execution_log = []
    
    def execute_actions(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute list of actions."""
        results = {
            "success": True,
            "total_actions": len(actions),
            "completed": 0,
            "failed": 0,
            "logs": []
        }
        
        for idx, action in enumerate(actions):
            try:
                action_type = action.get("action")
                params = action.get("params", {})
                
                log_entry = {
                    "step": idx + 1,
                    "action": action_type,
                    "params": params,
                    "status": "pending"
                }
                
                success = self._execute_single_action(action_type, params)
                
                if success:
                    log_entry["status"] = "success"
                    results["completed"] += 1
                else:
                    log_entry["status"] = "failed"
                    results["failed"] += 1
                    results["success"] = False
                
                results["logs"].append(log_entry)
                self.execution_log.append(log_entry)
                
            except Exception as e:
                log_entry["status"] = "error"
                log_entry["error"] = str(e)
                results["logs"].append(log_entry)
                results["failed"] += 1
                print(f"Action execution error: {e}")
        
        return results
    
    def _execute_single_action(self, action_type: str, params: Dict[str, Any]) -> bool:
        """Execute single action."""
        
        # Browser actions
        if action_type == "open_browser":
            return self.browser.start_browser()
        
        elif action_type == "navigate":
            url = params.get("url", "")
            return self.browser.navigate(url)
        
        elif action_type == "search_web":
            query = params.get("query", "")
            site = params.get("site", "google").lower()
            
            if site == "youtube":
                return self.browser.search_youtube(query)
            elif site == "google":
                return self.browser.search_google(query)
            else:
                return self.browser.search_google(query)
        
        elif action_type == "click":
            selector = params.get("selector", "")
            if selector == "first_video":
                # Already handled in search_youtube
                return True
            return self.browser.click_element(selector)
        
        elif action_type == "type_text":
            field = params.get("field", "")
            text = params.get("text", "")
            if field:
                return self.browser.fill_form(field, text)
            else:
                return self.system.type_text(text)
        
        elif action_type == "close_browser":
            self.browser.close_browser()
            return True
        
        # System actions
        elif action_type == "open_app":
            app_name = params.get("app_name", "")
            return self.system.open_application(app_name)
        
        elif action_type == "press_key":
            key = params.get("key", "")
            return self.system.press_key(key)
        
        elif action_type == "hotkey":
            keys = params.get("keys", [])
            return self.system.press_hotkey(*keys)
        
        elif action_type == "wait":
            seconds = params.get("seconds", 1)
            time.sleep(seconds)
            return True
        
        elif action_type == "screenshot":
            filename = params.get("filename", "screenshot.png")
            result = self.system.screenshot(filename)
            return result is not None
        
        else:
            print(f"Unknown action type: {action_type}")
            return False
    
    def cleanup(self):
        """Cleanup resources."""
        self.browser.close_browser()
