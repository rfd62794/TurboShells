import thorpy
import inspect

print("thorpy.init signature:")
try:
    print(inspect.signature(thorpy.init))
except Exception as e:
    print(e)
