# Errors

## Breeding Error

Traceback (most recent call last):
  File "C:\Users\Admin\OneDrive\Documents\GitHub\TurboShells\main.py", line 192, in <module>
    game.handle_input()
    ~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Admin\OneDrive\Documents\GitHub\TurboShells\main.py", line 126, in handle_input
    if self.breeding_manager.breed():
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\Admin\OneDrive\Documents\GitHub\TurboShells\managers\breeding_manager.py", line 83, in breed
    self.game_state.retired_roster.remove(parent_a)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
ValueError: list.remove(x): x not in list

C:\Users\Admin\OneDrive\Documents\GitHub\TurboShells>
