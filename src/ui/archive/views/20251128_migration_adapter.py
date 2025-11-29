"""Migration Adapter for TurboShells UI Migration

Provides gradual migration path from legacy PyGame views to ImGui panels.
Maintains feature parity during transition period.
"""

import pygame
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class MigrationState(Enum):
    """Migration state for views."""
    LEGACY_ONLY = "legacy_only"
    MIGRATING = "migrating"
    IMGUI_ONLY = "imgui_only"
    HYBRID = "hybrid"


@dataclass
class ViewMigration:
    """Represents migration status of a specific view."""
    view_name: str
    state: MigrationState
    legacy_function: Optional[Callable] = None
    imgui_panel: Optional['BasePanel'] = None
    migration_progress: float = 0.0  # 0.0 to 1.0
    feature_flags: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.feature_flags is None:
            self.feature_flags = {}


class MigrationAdapter:
    """Gradual migration adapter for existing views.
    
    Responsibilities:
    - Manage migration status of all views
    - Route rendering to appropriate system (legacy or ImGui)
    - Provide fallback mechanisms during migration
    - Track migration progress and feature parity
    - Enable A/B testing during transition
    
    This class enables safe, gradual migration from legacy PyGame views
    to new ImGui panels without breaking existing functionality.
    """
    
    def __init__(self):
        """Initialize the migration adapter."""
        self.legacy_views: Dict[str, Callable] = {}
        self.imgui_panels: Dict[str, 'BasePanel'] = {}
        self.migrations: Dict[str, ViewMigration] = {}
        self.global_migration_mode = MigrationState.LEGACY_ONLY
        self.feature_toggles: Dict[str, bool] = {}
        
        # Migration statistics
        self.migration_stats = {
            'total_views': 0,
            'migrated_views': 0,
            'in_progress': 0,
            'legacy_only': 0
        }
    
    def register_legacy_view(self, view_name: str, view_function: Callable) -> None:
        """Register existing PyGame view for gradual migration.
        
        Args:
            view_name: Name identifier for the view
            view_function: Legacy rendering function
        """
        self.legacy_views[view_name] = view_function
        
        # Create migration entry if not exists
        if view_name not in self.migrations:
            self.migrations[view_name] = ViewMigration(
                view_name=view_name,
                state=MigrationState.LEGACY_ONLY,
                legacy_function=view_function
            )
        
        self._update_stats()
    
    def register_imgui_panel(self, view_name: str, imgui_panel: 'BasePanel') -> None:
        """Register ImGui panel for view migration.
        
        Args:
            view_name: Name identifier for the view
            imgui_panel: ImGui panel implementation
        """
        self.imgui_panels[view_name] = imgui_panel
        
        # Update migration entry
        if view_name in self.migrations:
            migration = self.migrations[view_name]
            migration.imgui_panel = imgui_panel
            migration.state = MigrationState.HYBRID
        else:
            self.migrations[view_name] = ViewMigration(
                view_name=view_name,
                state=MigrationState.IMGUI_ONLY,
                imgui_panel=imgui_panel
            )
        
        self._update_stats()
    
    def migrate_view(self, view_name: str, target_state: MigrationState = MigrationState.IMGUI_ONLY) -> bool:
        """Mark view as migrated to specific state.
        
        Args:
            view_name: Name of view to migrate
            target_state: Target migration state
            
        Returns:
            True if migration was successful, False otherwise
        """
        if view_name not in self.migrations:
            print(f"Warning: View '{view_name}' not found for migration")
            return False
        
        migration = self.migrations[view_name]
        
        # Validate migration requirements
        if target_state == MigrationState.IMGUI_ONLY and migration.imgui_panel is None:
            print(f"Error: Cannot migrate '{view_name}' to ImGui-only - no ImGui panel registered")
            return False
        
        if target_state == MigrationState.LEGACY_ONLY and migration.legacy_function is None:
            print(f"Error: Cannot revert '{view_name}' to legacy-only - no legacy function available")
            return False
        
        migration.state = target_state
        migration.migration_progress = 1.0 if target_state == MigrationState.IMGUI_ONLY else 0.0
        
        self._update_stats()
        print(f"Migrated view '{view_name}' to {target_state.value}")
        return True
    
    def set_migration_progress(self, view_name: str, progress: float) -> None:
        """Set migration progress for a view.
        
        Args:
            view_name: Name of view
            progress: Progress value (0.0 to 1.0)
        """
        if view_name in self.migrations:
            self.migrations[view_name].migration_progress = max(0.0, min(1.0, progress))
    
    def set_feature_flag(self, view_name: str, feature: str, enabled: bool) -> None:
        """Enable/disable specific features during migration.
        
        Args:
            view_name: Name of view
            feature: Feature name
            enabled: Whether feature is enabled
        """
        if view_name in self.migrations:
            self.migrations[view_name].feature_flags[feature] = enabled
    
    def set_global_feature_toggle(self, feature: str, enabled: bool) -> None:
        """Set global feature toggle.
        
        Args:
            feature: Feature name
            enabled: Whether feature is enabled
        """
        self.feature_toggles[feature] = enabled
    
    def render_view(self, view_name: str, screen: pygame.Surface, font: pygame.font.Font, 
                    game_state: Any) -> None:
        """Render view using appropriate system based on migration state.
        
        Args:
            view_name: Name of view to render
            screen: PyGame surface for rendering
            font: Font for legacy rendering
            game_state: Current game state
        """
        migration = self.migrations.get(view_name)
        if not migration:
            print(f"Warning: View '{view_name}' not found")
            return
        
        # Determine rendering method based on migration state
        if migration.state == MigrationState.LEGACY_ONLY:
            self._render_legacy(view_name, screen, font, game_state)
        elif migration.state == MigrationState.IMGUI_ONLY:
            self._render_imgui(view_name, game_state)
        elif migration.state == MigrationState.HYBRID:
            self._render_hybrid(view_name, screen, font, game_state)
        elif migration.state == MigrationState.MIGRATING:
            self._render_migrating(view_name, screen, font, game_state)
    
    def _render_legacy(self, view_name: str, screen: pygame.Surface, font: pygame.font.Font, 
                      game_state: Any) -> None:
        """Render using legacy PyGame system.
        
        Args:
            view_name: Name of view
            screen: PyGame surface
            font: Font for rendering
            game_state: Current game state
        """
        legacy_func = self.legacy_views.get(view_name)
        if legacy_func:
            try:
                legacy_func(screen, font, game_state)
            except Exception as e:
                print(f"Error rendering legacy view '{view_name}': {e}")
    
    def _render_imgui(self, view_name: str, game_state: Any) -> None:
        """Render using ImGui system.
        
        Args:
            view_name: Name of view
            game_state: Current game state
        """
        panel = self.imgui_panels.get(view_name)
        if panel:
            try:
                panel.render(game_state)
            except Exception as e:
                print(f"Error rendering ImGui panel '{view_name}': {e}")
    
    def _render_hybrid(self, view_name: str, screen: pygame.Surface, font: pygame.font.Font, 
                      game_state: Any) -> None:
        """Render using hybrid approach (both systems).
        
        Args:
            view_name: Name of view
            screen: PyGame surface
            font: Font for rendering
            game_state: Current game state
        """
        migration = self.migrations[view_name]
        
        # Render legacy first
        if migration.legacy_function and migration.feature_flags.get('render_legacy', True):
            self._render_legacy(view_name, screen, font, game_state)
        
        # Then render ImGui overlay
        if migration.imgui_panel and migration.feature_flags.get('render_imgui', True):
            self._render_imgui(view_name, game_state)
    
    def _render_migrating(self, view_name: str, screen: pygame.Surface, font: pygame.font.Font, 
                         game_state: Any) -> None:
        """Render during migration state with progress indicator.
        
        Args:
            view_name: Name of view
            screen: PyGame surface
            font: Font for rendering
            game_state: Current game state
        """
        migration = self.migrations[view_name]
        
        # Render primary system based on progress
        if migration.migration_progress < 0.5:
            # Mostly legacy
            self._render_legacy(view_name, screen, font, game_state)
            
            # Show ImGui overlay if available
            if migration.imgui_panel and migration.feature_flags.get('show_preview', False):
                self._render_imgui(view_name, game_state)
        else:
            # Mostly ImGui
            self._render_imgui(view_name, game_state)
            
            # Show legacy fallback if needed
            if migration.legacy_function and migration.feature_flags.get('show_fallback', False):
                self._render_legacy(view_name, screen, font, game_state)
        
        # Show migration progress overlay (debug)
        if self.feature_toggles.get('show_migration_progress', False):
            self._render_migration_overlay(screen, font, migration)
    
    def _render_migration_overlay(self, screen: pygame.Surface, font: pygame.font.Font, 
                                 migration: ViewMigration) -> None:
        """Render migration progress overlay for debugging.
        
        Args:
            screen: PyGame surface
            font: Font for rendering
            migration: Migration information
        """
        # Simple progress indicator
        progress_text = f"Migrating {migration.view_name}: {migration.migration_progress:.1%}"
        text_surface = font.render(progress_text, True, (255, 255, 0))
        screen.blit(text_surface, (10, 10))
    
    def get_migration_status(self, view_name: str) -> Optional[ViewMigration]:
        """Get migration status for a specific view.
        
        Args:
            view_name: Name of view
            
        Returns:
            Migration information or None if not found
        """
        return self.migrations.get(view_name)
    
    def get_all_migration_status(self) -> Dict[str, ViewMigration]:
        """Get migration status for all views.
        
        Returns:
            Dictionary of all migration information
        """
        return self.migrations.copy()
    
    def get_migration_summary(self) -> Dict[str, Any]:
        """Get summary of migration progress.
        
        Returns:
            Dictionary with migration statistics
        """
        return {
            'total_views': len(self.migrations),
            'migrated_views': len([m for m in self.migrations.values() if m.state == MigrationState.IMGUI_ONLY]),
            'in_progress': len([m for m in self.migrations.values() if m.state == MigrationState.MIGRATING]),
            'legacy_only': len([m for m in self.migrations.values() if m.state == MigrationState.LEGACY_ONLY]),
            'hybrid': len([m for m in self.migrations.values() if m.state == MigrationState.HYBRID]),
            'overall_progress': self._calculate_overall_progress()
        }
    
    def _calculate_overall_progress(self) -> float:
        """Calculate overall migration progress.
        
        Returns:
            Overall progress percentage (0.0 to 1.0)
        """
        if not self.migrations:
            return 0.0
        
        total_progress = sum(m.migration_progress for m in self.migrations.values())
        return total_progress / len(self.migrations)
    
    def _update_stats(self) -> None:
        """Update migration statistics."""
        self.migration_stats = {
            'total_views': len(self.migrations),
            'migrated_views': len([m for m in self.migrations.values() if m.state == MigrationState.IMGUI_ONLY]),
            'in_progress': len([m for m in self.migrations.values() if m.state == MigrationState.MIGRATING]),
            'legacy_only': len([m for m in self.migrations.values() if m.state == MigrationState.LEGACY_ONLY])
        }
    
    def set_global_migration_mode(self, mode: MigrationState) -> None:
        """Set global migration mode for all views.
        
        Args:
            mode: Global migration mode
        """
        self.global_migration_mode = mode
        
        # Apply to all views that support it
        for view_name, migration in self.migrations.items():
            if mode == MigrationState.LEGACY_ONLY and migration.legacy_function:
                migration.state = MigrationState.LEGACY_ONLY
            elif mode == MigrationState.IMGUI_ONLY and migration.imgui_panel:
                migration.state = MigrationState.IMGUI_ONLY
            elif mode == MigrationState.HYBRID and migration.legacy_function and migration.imgui_panel:
                migration.state = MigrationState.HYBRID
    
    def validate_migration(self, view_name: str) -> List[str]:
        """Validate migration completeness and feature parity.
        
        Args:
            view_name: Name of view to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        migration = self.migrations.get(view_name)
        
        if not migration:
            issues.append(f"View '{view_name}' not found")
            return issues
        
        if migration.state == MigrationState.IMGUI_ONLY:
            if not migration.imgui_panel:
                issues.append("ImGui panel missing for ImGui-only migration")
        
        elif migration.state == MigrationState.LEGACY_ONLY:
            if not migration.legacy_function:
                issues.append("Legacy function missing for legacy-only migration")
        
        elif migration.state == MigrationState.HYBRID:
            if not migration.imgui_panel:
                issues.append("ImGui panel missing for hybrid migration")
            if not migration.legacy_function:
                issues.append("Legacy function missing for hybrid migration")
        
        return issues
    
    def print_migration_report(self) -> None:
        """Print detailed migration report."""
        summary = self.get_migration_summary()
        
        print("=== Migration Adapter Report ===")
        print(f"Total Views: {summary['total_views']}")
        print(f"Migrated: {summary['migrated_views']}")
        print(f"In Progress: {summary['in_progress']}")
        print(f"Legacy Only: {summary['legacy_only']}")
        print(f"Hybrid: {summary['hybrid']}")
        print(f"Overall Progress: {summary['overall_progress']:.1%}")
        print()
        
        print("View Details:")
        for view_name, migration in self.migrations.items():
            issues = self.validate_migration(view_name)
            status = "OK" if not issues else f"ISSUES ({len(issues)})"
            print(f"  {view_name}: {migration.state.value} - {status}")
            if issues:
                for issue in issues:
                    print(f"    - {issue}")
        
        print("=" * 40)
