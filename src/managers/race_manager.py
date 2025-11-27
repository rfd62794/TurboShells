from game.game_state import generate_random_turtle, generate_balanced_opponent
from settings import *
import ui.layout as layout
from game.race_track import generate_track, get_terrain_at
from core.monitoring_system import monitoring_system
from core.racing.terrain_system import terrain_generator, terrain_renderer


class RaceManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.results = []

    def start_race(self):
        print(f"[DEBUG] RaceManager.start_race() called")
        self.results = []
        self.game_state.race_results = []
        
        # Handle betting: deduct current bet upfront if affordable
        self.bet_amount = 0
        bet = getattr(self.game_state, "current_bet", 0)
        print(f"[DEBUG] Current bet: ${bet}, Player money: ${self.game_state.money}")
        
        if bet > 0 and self.game_state.money >= bet:
            self.bet_amount = bet
            self.game_state.money -= bet
            print(f"[DEBUG] Bet deducted: ${self.bet_amount}, Remaining money: ${self.game_state.money}")
        elif bet > 0 and self.game_state.money < bet:
            # Not enough money; clear the bet
            self.game_state.current_bet = 0
            print(f"[DEBUG] Not enough money for bet, bet cleared")
            
        # Generate a new track for this race
        self.track = generate_track(TRACK_LENGTH_LOGIC)
        print(f"[DEBUG] Track generated with {len(self.track)} segments")

        # Get player's turtle for balanced opponent generation
        player_idx = getattr(self.game_state, "active_racer_index", 0)
        print(f"[DEBUG] Player active_racer_index: {player_idx}")
        
        player_turtle = (
            self.game_state.roster[player_idx]
            if player_idx < len(self.game_state.roster)
            else None
        )
        
        print(f"[DEBUG] Player turtle found: {player_turtle.name if player_turtle else None}")

        # Create race roster: player turtle + 2 temporary opponents
        self.race_roster = []

        # Add player's selected turtle (copy to avoid modifying original)
        if player_turtle:
            # Create a copy of the player turtle for the race
            import copy

            race_player = copy.deepcopy(player_turtle)
            race_player.reset_for_race()
            self.race_roster.append(race_player)
            print(f"[DEBUG] Player turtle added to race: {race_player.name}")

        # Generate 2 balanced opponents
        if player_turtle:
            print(f"[DEBUG] About to generate 2 opponents for player {player_turtle.name}")
            for i in range(2):
                print(f"[DEBUG] Generating opponent {i+1}...")
                opponent = generate_balanced_opponent(player_turtle)
                opponent.is_temp = True
                opponent.reset_for_race()
                self.race_roster.append(opponent)
                print(f"[DEBUG] Opponent {i+1} generated: {opponent.name} (speed: {opponent.stats['speed']}, energy: {opponent.stats['max_energy']})")
        else:
            print(f"[ERROR] No player turtle available, cannot generate opponents")
            
        print(f"[DEBUG] Final race roster: {len(self.race_roster)} turtles")
        for i, turtle in enumerate(self.race_roster):
            print(f"[DEBUG]   {i}: {turtle.name} (speed: {turtle.stats['speed']}, energy: {turtle.stats['max_energy']})")
        
        # Generate terrain for this race
        print(f"[DEBUG] Generating terrain for race...")
        terrain_segments = terrain_generator.generate_terrain(difficulty="normal")
        terrain_renderer.set_terrain(terrain_segments)
        print(f"[DEBUG] Generated {len(terrain_segments)} terrain segments")

    def handle_click(self, pos):
        """Handle mouse clicks on the Race HUD (speed controls)."""
        if layout.SPEED_1X_RECT.collidepoint(pos):
            self.game_state.race_speed_multiplier = 1
        elif layout.SPEED_2X_RECT.collidepoint(pos):
            self.game_state.race_speed_multiplier = 2
        elif layout.SPEED_4X_RECT.collidepoint(pos):
            self.game_state.race_speed_multiplier = 4

    def update(self):
        active_turtles = self.race_roster if hasattr(self, "race_roster") else []

        for _ in range(self.game_state.race_speed_multiplier):
            for t in active_turtles:
                # 1. Determine Terrain using shared RaceTrack helper
                terrain = get_terrain_at(self.track, t.race_distance)

                # 2. UPDATE PHYSICS (Using the Shared Class)
                move_amt = t.update_physics(terrain)
                t.race_distance += move_amt

                # 3. Check Finish
                if t.race_distance >= TRACK_LENGTH_LOGIC and not t.finished:
                    t.finished = True
                    t.rank = len(self.results) + 1
                    self.results.append(t)

        # Sync results
        self.game_state.race_results = self.results

        # Check if Race Over (All finished)
        if len(self.results) == len(active_turtles):
            self.process_rewards()
            return True  # Race Finished
        return False

    def process_rewards(self):
        # Find player rank based on selected active racer
        idx = getattr(self.game_state, "active_racer_index", 0)
        player_turtle = None
        if 0 <= idx < len(self.game_state.roster):
            player_turtle = self.game_state.roster[idx]

        # Find the player's race turtle by name (since race uses copies)
        player_race_turtle = None
        if player_turtle:
            for race_turtle in self.results:
                if race_turtle.name == player_turtle.name:
                    player_race_turtle = race_turtle
                    break

        if player_race_turtle:
            rank = player_race_turtle.rank
            reward = 0
            if rank == 1:
                reward = REWARD_1ST
            elif rank == 2:
                reward = REWARD_2ND
            elif rank == 3:
                reward = REWARD_3RD
            else:
                # Participation reward for showing up
                reward = REWARD_PARTICIPATION

            # Betting payout: simple 2x on win if first place
            payout = 0
            if rank == 1 and self.bet_amount > 0:
                payout = self.bet_amount * 2

            self.game_state.money += reward + payout
            print(f"Player finished {rank}. Reward: ${reward} | Bet Payout: ${payout}")

            # Record race result in player's history (update original turtle)
            total_earnings = reward + payout
            player_turtle.add_race_result(rank, total_earnings)
            
            # Track race statistics in monitoring system
            monitoring_system.stats_tracker.record_race_result(
                won=(rank == 1),
                earnings=total_earnings,
                position=rank
            )

            # Auto-save after race completion
            self.game_state.auto_save("race_completion")

        # Post-race cleanup: recover energy and age turtles
        for i, t in enumerate(self.game_state.roster):
            if not t:
                continue
            # Energy is only used for the race; recover fully afterwards
            t.current_energy = t.stats["max_energy"]

            # Aging: each completed race counts as 1 day
            t.age += 1
            if t.age >= MAX_AGE and t.is_active:
                # Auto-retire to retired_roster
                t.is_active = False
                self.game_state.roster[i] = None
                self.game_state.retired_roster.append(t)

    def handle_result_click(self, pos):
        if layout.RACE_RESULT_MENU_BTN_RECT.collidepoint(pos):
            return "GOTO_MENU"
        if layout.RACE_RESULT_RERUN_BTN_RECT.collidepoint(pos):
            self.start_race()
            return "RERUN"
        return None
