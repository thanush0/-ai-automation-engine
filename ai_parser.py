import json
import re
from typing import List, Dict, Any
from openai import OpenAI
import requests

class AIParser:
    def __init__(self, use_local_llm=False):
        self.use_local_llm = use_local_llm
        if not use_local_llm:
            from config import config
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            from config import config
            self.ollama_url = config.OLLAMA_BASE_URL
            self.model = config.OLLAMA_MODEL
    
    def parse_command(self, user_input: str) -> List[Dict[str, Any]]:
        """Parse natural language command into structured actions."""
        
        system_prompt = """You are an automation parser. Convert user commands into JSON actions.

Available action types:
- open_browser: Open web browser
- navigate: Go to URL
- search_web: Search on a website
- click: Click element
- type_text: Type text into field
- open_app: Open application
- press_key: Press keyboard key
- wait: Wait for seconds
- close_browser: Close browser

Return ONLY valid JSON array of actions. Example:
[
  {"action": "open_browser", "params": {}},
  {"action": "navigate", "params": {"url": "https://youtube.com"}},
  {"action": "search_web", "params": {"query": "songs", "site": "youtube"}},
  {"action": "click", "params": {"selector": "first_video"}},
  {"action": "press_key", "params": {"key": "space"}}
]

User command: {command}

Return JSON array:"""

        if self.use_local_llm:
            response = self._query_ollama(system_prompt.format(command=user_input))
        else:
            response = self._query_openai(system_prompt.format(command=user_input))
        
        return self._extract_json(response)
    
    def _query_openai(self, prompt: str) -> str:
        """Query OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an automation command parser. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._fallback_parse(prompt)
    
    def _query_ollama(self, prompt: str) -> str:
        """Query local Ollama LLM."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            return response.json().get("response", "")
        except Exception as e:
            print(f"Ollama error: {e}")
            return self._fallback_parse(prompt)
    
    def _extract_json(self, response: str) -> List[Dict[str, Any]]:
        """Extract JSON from LLM response."""
        try:
            # Try to find JSON array in response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response)
        except Exception as e:
            print(f"JSON parse error: {e}")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, user_input: str) -> List[Dict[str, Any]]:
        """Simple rule-based fallback parser."""
        actions = []
        lower_input = user_input.lower()
        
        # Open browser
        if "chrome" in lower_input or "browser" in lower_input:
            actions.append({"action": "open_browser", "params": {}})
        
        # Navigate to sites
        if "youtube" in lower_input:
            actions.append({"action": "navigate", "params": {"url": "https://youtube.com"}})
            
            if "search" in lower_input or "play" in lower_input:
                # Extract search query
                query = "songs"  # Default
                if "search" in lower_input:
                    parts = lower_input.split("search")
                    if len(parts) > 1:
                        query = parts[1].strip().split()[0:3]
                        query = " ".join(query)
                
                actions.append({"action": "search_web", "params": {"query": query, "site": "youtube"}})
                actions.append({"action": "click", "params": {"selector": "first_video"}})
        
        # Train booking
        if "train" in lower_input or "irctc" in lower_input:
            actions.append({"action": "navigate", "params": {"url": "https://www.irctc.co.in"}})
            actions.append({"action": "type_text", "params": {"field": "from", "text": "Chennai"}})
            actions.append({"action": "type_text", "params": {"field": "to", "text": "Bangalore"}})
        
        # Open applications
        if "notepad" in lower_input:
            actions.append({"action": "open_app", "params": {"app_name": "notepad"}})
        
        return actions if actions else [{"action": "error", "params": {"message": "Could not parse command"}}]
