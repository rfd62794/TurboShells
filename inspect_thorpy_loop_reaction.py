import thorpy
import inspect

print("thorpy.Loop.reaction signature:")
try:
    print(inspect.signature(thorpy.Loop.reaction))
except Exception as e:
    print(e)
