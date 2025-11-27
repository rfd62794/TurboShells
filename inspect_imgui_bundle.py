import imgui_bundle
import inspect

print("imgui_bundle contents:")
print(dir(imgui_bundle))

try:
    from imgui_bundle import python_backends
    print("\npython_backends contents:")
    print(dir(python_backends))
    
    try:
        from imgui_bundle.python_backends import pygame_backend
        print("\npygame_backend contents:")
        print(dir(pygame_backend))
    except ImportError:
        print("\nNo pygame_backend found")
        
except ImportError:
    print("\nNo python_backends found")
