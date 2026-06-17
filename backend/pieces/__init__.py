import os
import importlib
import inspect

# Cache for loaded pieces
PIECES_REGISTRY = {}

def load_all_pieces():
    """Dynamically scan the pieces directory and load all actions and schemas."""
    global PIECES_REGISTRY
    PIECES_REGISTRY = {}
    
    current_dir = os.path.dirname(__file__)
    if not os.path.exists(current_dir):
        return
        
    for item in os.listdir(current_dir):
        piece_dir = os.path.join(current_dir, item)
        if os.path.isdir(piece_dir) and not item.startswith("__"):
            # Attempt to import the piece module
            try:
                module = importlib.import_module(f"pieces.{item}")
                
                # Each piece should define a PIECE_MANIFEST dict
                if hasattr(module, "PIECE_MANIFEST"):
                    manifest = getattr(module, "PIECE_MANIFEST")
                    # Register actions
                    for action_id, action_data in manifest.get("actions", {}).items():
                        PIECES_REGISTRY[action_id] = action_data
            except Exception as e:
                print(f"[PieceLoader] Error loading piece {item}: {e}")

# Load them on initialization
load_all_pieces()

def get_piece_action(action_id: str):
    """Retrieve an action from the loaded pieces."""
    return PIECES_REGISTRY.get(action_id)
