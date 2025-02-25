import json
from typing import Any, Dict


def update_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the preferences in the preferences.json file.
    
    Args:
        preferences: Dictionary containing the new preferences to update
        
    Returns:
        Dict containing the updated preferences
    """
    preferences_file_path = "preferences.json"
    
    try:
        # Read current preferences
        with open(preferences_file_path, 'r') as f:
            current_preferences = json.load(f)
        
        # Update preferences
        current_preferences["preferences"].update(preferences)
        
        # Write updated preferences back to file
        with open(preferences_file_path, 'w') as f:
            json.dump(current_preferences, f, indent=4)
            
        return current_preferences["preferences"]
    
    except Exception as e:
        return {"error": f"Failed to update preferences: {str(e)}"} 