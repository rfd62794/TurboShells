"""SceneController orchestrates panel visibility using UIManager and UI events."""

from typing import Dict, Optional

from settings import STATE_MENU


class SceneController:
    """Central coordinator for state-driven panel visibility."""

    def __init__(self, ui_manager, event_bus, state_to_panel: Dict[str, str]):
        self.ui_manager = ui_manager
        self.event_bus = event_bus
        self.state_to_panel = state_to_panel
        self.current_state: Optional[str] = None

        # Listen for UI navigation events
        self.event_bus.subscribe("ui:navigate", self._on_navigate)
        self.event_bus.subscribe("ui:panel_closed", self._on_panel_closed)

    def shutdown(self):
        self.event_bus.unsubscribe("ui:navigate", self._on_navigate)
        self.event_bus.unsubscribe("ui:panel_closed", self._on_panel_closed)

    def goto_state(self, state: str):
        if state == self.current_state:
            print(f"[SceneController] Already in state '{state}', skipping")
            return
        print(f"[SceneController] Transitioning from '{self.current_state}' to '{state}'")
        self._hide_current_panel()
        self.current_state = state
        self._show_panel_for_state(state)

    def _show_panel_for_state(self, state: str):
        panel_id = self.state_to_panel.get(state)
        if panel_id:
            print(f"[SceneController] Showing panel '{panel_id}' for state '{state}'")
            self.ui_manager.show_panel(panel_id)
        else:
            print(f"[SceneController] No panel mapped for state '{state}'")

    def _hide_current_panel(self):
        if not self.current_state:
            return
        panel_id = self.state_to_panel.get(self.current_state)
        if panel_id:
            print(f"[SceneController] Hiding panel '{panel_id}' for previous state '{self.current_state}'")
            self.ui_manager.hide_panel(panel_id)

    # Event handlers -----------------------------------------------------
    def _on_navigate(self, payload):
        target_state = payload.get("state")
        print(f"[SceneController] Received navigate event to '{target_state}'")
        if target_state:
            self.goto_state(target_state)

    def _on_panel_closed(self, payload):
        panel_id = payload.get("panel_id")
        print(f"[SceneController] Panel '{panel_id}' closed")
        if payload.get("panel_id") == self.state_to_panel.get(self.current_state):
            # Default fallback to main menu when current panel closes
            print(f"[SceneController] Current panel closed, falling back to main menu")
            self.goto_state(STATE_MENU)
