import thorpy
import inspect

print("thorpy.Loop signature:")
try:
    print(inspect.signature(thorpy.Loop))
except Exception as e:
    print(e)

print("\nthorpy.Loop doc:")
print(thorpy.Loop.__doc__)
