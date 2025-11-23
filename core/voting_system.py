"""
Voting System for TurboShells
Complete design voting system with player-exclusive voting and genetic impact
"""

import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from .visual_genetics import VisualGenetics


class DesignPackage:
    """
    Complete design package for voting
    Contains genetics, SVG content, feature breakdown, and voting data
    """
    
    def __init__(self, design_id: str, visual_genetics: Dict[str, Any], 
                 svg_content: str, feature_breakdown: Dict[str, Any]):
        self.id = design_id
        self.genetics = visual_genetics
        self.svg_content = svg_content
        self.feature_breakdown = feature_breakdown
        self.rating_categories = self._get_rating_categories()
        self.voting_status = 'pending'  # pending, completed
        self.reward_available = True
        self.ratings = {}
        self.timestamp = datetime.now()
        self.genetic_impact = None
    
    def _get_rating_categories(self) -> Dict[str, Dict[str, Any]]:
        """
        Define rating categories for voting
        """
        return {
            'overall': {
                'display_name': 'Overall Design',
                'type': 'rating_1_5',
                'weight': 1.0,
                'description': 'Your overall impression of this turtle design'
            },
            'shell_appearance': {
                'display_name': 'Shell Appearance',
                'type': 'rating_1_5',
                'weight': 0.9,
                'description': 'How the shell looks (color, pattern, size)'
            },
            'color_harmony': {
                'display_name': 'Color Harmony',
                'type': 'rating_1_5',
                'weight': 0.8,
                'description': 'How well the colors work together'
            },
            'pattern_quality': {
                'display_name': 'Pattern Quality',
                'type': 'rating_1_5',
                'weight': 0.7,
                'description': 'How good the patterns look'
            },
            'proportions': {
                'display_name': 'Body Proportions',
                'type': 'rating_1_5',
                'weight': 0.6,
                'description': 'How well-proportioned the turtle is'
            }
        }
    
    def is_available_for_voting(self) -> bool:
        """Check if design is available for voting"""
        return self.voting_status == 'pending' and self.reward_available
    
    def can_earn_reward(self) -> bool:
        """Check if reward is available"""
        return self.reward_available and self.voting_status == 'pending'
    
    def complete_voting(self, ratings: Dict[str, float], genetic_impact: Dict[str, Any]):
        """Mark voting as complete with results"""
        self.voting_status = 'completed'
        self.ratings = ratings
        self.genetic_impact = genetic_impact
        self.reward_available = False


class VotingSystem:
    """
    Complete voting system for design evaluation
    Handles daily design generation, voting processing, and genetic impact
    """
    
    def __init__(self):
        self.daily_designs: List[DesignPackage] = []
        self.voting_history: List[Dict[str, Any]] = []
        self.genetic_pool_manager = None  # Will be set later
        self.last_reset_date: Optional[date] = None
        
        # System components
        self.visual_genetics = VisualGenetics()
        # SVG generator no longer needed - using direct renderer
        
        # Configuration
        self.daily_design_count = 5
        self.reward_per_vote = 1  # $1 per completed vote
        self.rating_range = (1, 5)
        
        # Statistics
        self.stats = {
            'total_votes_cast': 0,
            'total_rewards_earned': 0,
            'designs_generated': 0,
            'voting_sessions': 0,
            'average_rating': 0.0
        }
    
    def set_genetic_pool_manager(self, manager):
        """Set genetic pool manager for impact processing"""
        self.genetic_pool_manager = manager
    
    def generate_daily_designs(self) -> List[DesignPackage]:
        """
        Generate 5 new designs for daily voting
        Returns list of DesignPackage objects
        """
        today = date.today()
        
        # Check if we need new designs
        if self.last_reset_date == today and self.daily_designs:
            return self.daily_designs
        
        # Generate new designs
        self.daily_designs = []
        
        for i in range(self.daily_design_count):
            # Generate random genetics
            random_genetics = self.visual_genetics.generate_random_genetics()
            
            # Generate SVG (no longer needed - using direct renderer)
            svg_content = ""  # Empty since we're not using SVG
            
            # Create feature breakdown
            feature_breakdown = self._create_feature_breakdown(random_genetics)
            
            # Create design package
            design = DesignPackage(
                f"design_{today.strftime('%Y%m%d')}_{i}",
                random_genetics,
                svg_content,
                feature_breakdown
            )
            
            self.daily_designs.append(design)
        
        self.last_reset_date = today
        self.stats['designs_generated'] += self.daily_design_count
        
        return self.daily_designs
    
    def _create_feature_breakdown(self, genetics: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Create detailed feature breakdown for voting
        """
        return {
            'shell_color': {
                'gene_name': 'shell_base_color',
                'display_name': 'Shell Color',
                'value': genetics.get('shell_base_color', (34, 139, 34)),
                'type': 'color',
                'description': 'Primary shell color',
                'rating_weight': 1.0
            },
            'shell_pattern': {
                'gene_name': 'shell_pattern_type',
                'display_name': 'Shell Pattern',
                'value': genetics.get('shell_pattern_type', 'stripes'),
                'type': 'pattern',
                'description': 'Shell pattern style',
                'rating_weight': 0.8
            },
            'shell_pattern_color': {
                'gene_name': 'shell_pattern_color',
                'display_name': 'Pattern Color',
                'value': genetics.get('shell_pattern_color', (255, 255, 255)),
                'type': 'color',
                'description': 'Shell pattern color',
                'rating_weight': 0.6
            },
            'body_color': {
                'gene_name': 'body_base_color',
                'display_name': 'Body Color',
                'value': genetics.get('body_base_color', (107, 142, 35)),
                'type': 'color',
                'description': 'Primary body color',
                'rating_weight': 0.8
            },
            'proportions': {
                'gene_name': 'combined_proportions',
                'display_name': 'Body Proportions',
                'value': {
                    'shell_size': genetics.get('shell_size_modifier', 1.0),
                    'head_size': genetics.get('head_size_modifier', 1.0),
                    'leg_length': genetics.get('leg_length', 1.0)
                },
                'type': 'proportions',
                'description': 'Overall body proportions',
                'rating_weight': 0.6
            }
        }
    
    def submit_ratings(self, design_id: str, ratings: Dict[str, float]) -> Dict[str, Any]:
        """
        Process player ratings for a design
        Returns result with reward and genetic impact
        """
        # Find design
        design = self._find_design(design_id)
        if not design:
            return {"error": "Design not found"}
        
        if design.voting_status == 'completed':
            return {"error": "Already voted on this design"}
        
        # Validate ratings
        validated_ratings = self._validate_ratings(ratings)
        
        # Record ratings
        rating_record = {
            'design_id': design_id,
            'timestamp': datetime.now(),
            'ratings': validated_ratings,
            'genetics': design.genetics
        }
        
        self.voting_history.append(rating_record)
        
        # Apply to genetic pool
        genetic_impact = {}
        if self.genetic_pool_manager:
            genetic_impact = self.genetic_pool_manager.apply_ratings_to_pool(
                design.genetics, validated_ratings
            )
        
        # Award reward
        reward_earned = self.reward_per_vote
        self._award_money_to_player(reward_earned)
        
        # Update design status
        design.complete_voting(validated_ratings, genetic_impact)
        
        # Update statistics
        self._update_statistics(validated_ratings)
        
        return {
            'success': True,
            'reward_earned': reward_earned,
            'genetic_impact': genetic_impact,
            'message': f"You earned ${reward_earned} and influenced future turtle genetics!"
        }
    
    def _find_design(self, design_id: str) -> Optional[DesignPackage]:
        """Find design by ID"""
        for design in self.daily_designs:
            if design.id == design_id:
                return design
        return None
    
    def _validate_ratings(self, ratings: Dict[str, float]) -> Dict[str, float]:
        """Validate and normalize ratings"""
        validated = {}
        
        for category, rating in ratings.items():
            if isinstance(rating, (int, float)) and self.rating_range[0] <= rating <= self.rating_range[1]:
                validated[category] = float(rating)
            else:
                validated[category] = 3.0  # Default to neutral
        
        return validated
    
    def _award_money_to_player(self, amount: int):
        """Integrate with game economy system"""
        # This would connect to the main game's money system
        print(f"Awarding ${amount} to player")
        # In actual implementation: game_state.player_money += amount
        self.stats['total_rewards_earned'] += amount
    
    def _update_statistics(self, ratings: Dict[str, float]):
        """Update voting statistics"""
        self.stats['total_votes_cast'] += 1
        
        # Update average rating
        if 'overall' in ratings:
            current_avg = self.stats['average_rating']
            new_avg = ((current_avg * (self.stats['total_votes_cast'] - 1)) + ratings['overall']) / self.stats['total_votes_cast']
            self.stats['average_rating'] = new_avg
    
    def get_daily_status(self) -> Dict[str, Any]:
        """Get current daily voting status"""
        total_designs = len(self.daily_designs)
        completed_votes = sum(1 for d in self.daily_designs if d.voting_status == 'completed')
        available_rewards = sum(1 for d in self.daily_designs if d.reward_available)
        
        return {
            'total_designs': total_designs,
            'completed_votes': completed_votes,
            'available_rewards': available_rewards,
            'potential_earnings': available_rewards * self.reward_per_vote,
            'completion_percentage': (completed_votes / total_designs) * 100 if total_designs > 0 else 0,
            'last_reset': self.last_reset_date,
            'days_until_reset': self._days_until_reset()
        }
    
    def _days_until_reset(self) -> int:
        """Calculate days until next reset"""
        if self.last_reset_date is None:
            return 0
        
        tomorrow = date.today() + timedelta(days=1)
        reset_date = date(tomorrow.year, tomorrow.month, tomorrow.day)
        return (reset_date - date.today()).days
    
    def get_voting_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get voting history with limit"""
        return self.voting_history[-limit:] if self.voting_history else []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive voting statistics"""
        return {
            **self.stats,
            'daily_status': self.get_daily_status(),
            'total_designs_voted': len(self.voting_history),
            'unique_designs_rated': len(set(record['design_id'] for record in self.voting_history)),
            'average_session_length': self._calculate_average_session_length(),
            'most_common_rating': self._get_most_common_rating()
        }
    
    def _calculate_average_session_length(self) -> float:
        """Calculate average number of votes per voting session"""
        if not self.voting_history:
            return 0.0
        
        # Group votes by date
        votes_by_date = {}
        for record in self.voting_history:
            vote_date = record['timestamp'].date()
            if vote_date not in votes_by_date:
                votes_by_date[vote_date] = 0
            votes_by_date[vote_date] += 1
        
        # Calculate average
        if votes_by_date:
            return sum(votes_by_date.values()) / len(votes_by_date)
        return 0.0
    
    def _get_most_common_rating(self) -> float:
        """Get most common overall rating"""
        overall_ratings = [record['ratings'].get('overall', 3.0) for record in self.voting_history if 'overall' in record['ratings']]
        
        if not overall_ratings:
            return 3.0
        
        # Count frequency
        rating_counts = {}
        for rating in overall_ratings:
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        # Find most common
        most_common = max(rating_counts.items(), key=lambda x: x[1])[0]
        return most_common
    
    def get_design_by_index(self, index: int) -> Optional[DesignPackage]:
        """Get design by index"""
        if 0 <= index < len(self.daily_designs):
            return self.daily_designs[index]
        return None
    
    def get_next_pending_design(self, current_index: int) -> Optional[DesignPackage]:
        """Get next pending design after current index"""
        for i in range(current_index + 1, len(self.daily_designs)):
            if self.daily_designs[i].is_available_for_voting():
                return self.daily_designs[i]
        return None
    
    def get_previous_pending_design(self, current_index: int) -> Optional[DesignPackage]:
        """Get previous pending design before current index"""
        for i in range(current_index - 1, -1, -1):
            if self.daily_designs[i].is_available_for_voting():
                return self.daily_designs[i]
        return None
    
    def reset_daily_designs(self) -> bool:
        """Force reset of daily designs"""
        self.daily_designs.clear()
        self.last_reset_date = None
        self.generate_daily_designs()
        return True
    
    def export_voting_data(self) -> Dict[str, Any]:
        """Export voting data for backup or analysis"""
        return {
            'daily_designs': [
                {
                    'id': design.id,
                    'genetics': design.genetics,
                    'ratings': design.ratings,
                    'voting_status': design.voting_status,
                    'timestamp': design.timestamp.isoformat()
                }
                for design in self.daily_designs
            ],
            'voting_history': [
                {
                    'design_id': record['design_id'],
                    'ratings': record['ratings'],
                    'timestamp': record['timestamp'].isoformat()
                }
                for record in self.voting_history
            ],
            'statistics': self.get_statistics(),
            'last_reset': self.last_reset_date.isoformat() if self.last_reset_date else None
        }
    
    def import_voting_data(self, data: Dict[str, Any]) -> bool:
        """Import voting data from backup"""
        try:
            # Import daily designs
            self.daily_designs.clear()
            for design_data in data.get('daily_designs', []):
                # Recreate design package
                feature_breakdown = self._create_feature_breakdown(design_data['genetics'])
                design = DesignPackage(
                    design_data['id'],
                    design_data['genetics'],
                    "",  # SVG content would need to be regenerated
                    feature_breakdown
                )
                design.ratings = design_data.get('ratings', {})
                design.voting_status = design_data.get('voting_status', 'pending')
                design.timestamp = datetime.fromisoformat(design_data['timestamp'])
                
                self.daily_designs.append(design)
            
            # Import voting history
            self.voting_history = []
            for record in data.get('voting_history', []):
                record['timestamp'] = datetime.fromisoformat(record['timestamp'])
                self.voting_history.append(record)
            
            # Import last reset date
            last_reset = data.get('last_reset')
            if last_reset:
                self.last_reset_date = datetime.fromisoformat(last_reset).date()
            
            return True
            
        except Exception as e:
            print(f"Error importing voting data: {e}")
            return False
    
    def validate_system_integrity(self) -> Dict[str, bool]:
        """Validate system integrity"""
        validation = {
            'daily_designs_valid': True,
            'voting_history_valid': True,
            'genetic_pool_connected': self.genetic_pool_manager is not None,
            'components_available': True
        }
        
        # Validate daily designs
        for design in self.daily_designs:
            if not design.genetics or not design.feature_breakdown:
                validation['daily_designs_valid'] = False
                break
        
        # Validate voting history
        for record in self.voting_history:
            if not record.get('design_id') or not record.get('ratings'):
                validation['voting_history_valid'] = False
                break
        
        # Validate components
        try:
            self.visual_genetics.generate_random_genetics()
            # Direct renderer test not needed here
        except:
            validation['components_available'] = False
        
        validation['overall'] = all(validation.values())
        return validation


# Factory function for easy instantiation
def create_voting_system() -> VotingSystem:
    """Create a VotingSystem instance"""
    return VotingSystem()


# Utility functions
def get_daily_designs() -> List[DesignPackage]:
    """Get daily designs using default voting system"""
    system = VotingSystem()
    return system.generate_daily_designs()


def submit_design_ratings(design_id: str, ratings: Dict[str, float]) -> Dict[str, Any]:
    """Submit ratings using default voting system"""
    system = VotingSystem()
    return system.submit_ratings(design_id, ratings)


def get_voting_status() -> Dict[str, Any]:
    """Get voting status using default voting system"""
    system = VotingSystem()
    return system.get_daily_status()
