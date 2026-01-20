"""
Prompt storage module for managing system prompts.
This is a stub implementation for the Django migration.
In the final Django version, prompts should be stored in the SystemPrompt model.
"""

import json
import os


class PromptStorage:
    """Simple in-memory prompt storage with JSON file backup"""
    
    def __init__(self):
        """Initialize prompt storage"""
        self.prompts = {}
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'configuration',
            'prompts.json'
        )
        self._load_prompts()
    
    def _load_prompts(self):
        """Load prompts from configuration file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.prompts = json.load(f)
        except Exception:
            self.prompts = {}
    
    def _save_prompts(self):
        """Save prompts to configuration file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.prompts, f, indent=2)
        except Exception:
            pass
    
    def get_prompt(self, store_id):
        """Get system prompt for a store"""
        return self.prompts.get(store_id, '')
    
    def set_prompt(self, store_id, content):
        """Set system prompt for a store"""
        self.prompts[store_id] = content
        self._save_prompts()
    
    def delete_prompt(self, store_id):
        """Delete system prompt for a store"""
        if store_id in self.prompts:
            del self.prompts[store_id]
            self._save_prompts()


# Global instance
_prompt_storage = None


def get_prompt_storage():
    """Get or create the global prompt storage instance"""
    global _prompt_storage
    if _prompt_storage is None:
        _prompt_storage = PromptStorage()
    return _prompt_storage
