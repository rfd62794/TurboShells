import thorpy
import inspect

print("thorpy.Box signature:")
try:
    print(inspect.signature(thorpy.Box))
except Exception as e:
    print(e)

print("\nthorpy.Box doc:")
print(thorpy.Box.__doc__)
