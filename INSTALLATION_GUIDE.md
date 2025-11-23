# TurboShells Visual Genetics System - Installation Guide

## Quick Installation

### Prerequisites
- Python 3.8 or higher
- PyGame (pygame-ce) for game interface

### Step 1: Install Dependencies
```bash
# Install the visual genetics dependencies
pip install -r requirements_visual_genetics.txt

# Or install manually:
pip install drawsvg svgwrite pygame-ce
```

### Step 2: Verify Installation
```bash
# Run the integration tests
python tests/test_visual_genetics_integration.py

# Expected output: "Overall: 8/8 tests passed"
```

### Step 3: Run the Demo
```bash
# Launch the interactive demo
python demo_visual_genetics.py
```

## Demo Controls
- **LEFT/RIGHT ARROWS**: Navigate between designs
- **SPACE**: Vote for current design
- **ESC**: Exit demo

## Dependencies Explained

### Required Dependencies
- **drawsvg**: SVG generation and manipulation
- **svgwrite**: SVG file creation and editing
- **pygame-ce**: Game interface and rendering

### Optional Dependencies
- **cairosvg**: Advanced SVG to PNG conversion (requires Cairo library)
- **pillow**: Image processing (required for cairosvg)

## Troubleshooting

### Common Issues

#### 1. Cairo Library Error
If you see errors about `libcairo-2.dll`, the system is using the fallback renderer. This is normal and expected on Windows systems without Cairo installed.

**Solution**: The system automatically falls back to the simple renderer which works without Cairo.

#### 2. Unicode Encoding Errors
If you see encoding errors in the console output, the system will work but console display may be limited.

**Solution**: This is a Windows console limitation and doesn't affect functionality.

#### 3. PyGame Installation
If pygame-ce installation fails, try:
```bash
pip install pygame-ce --only-binary=:all:
```

## System Requirements

### Minimum Requirements
- **Python**: 3.8+
- **Memory**: 512MB RAM
- **Storage**: 50MB free space

### Recommended Requirements
- **Python**: 3.10+
- **Memory**: 1GB RAM
- **Storage**: 100MB free space

## Performance Notes

### Rendering Performance
- **SVG Generation**: < 100ms per turtle
- **Caching**: Intelligent LRU cache for repeated renders
- **Memory**: Automatic cache management

### Game Integration
- **Frame Rate**: 60 FPS target
- **Render Time**: < 16ms per frame
- **Cache Hit Rate**: > 90% for repeated designs

## Advanced Installation

### Installing Cairo (Optional)
For advanced SVG features, you can install Cairo:

**Windows:**
1. Download Cairo from GTK+ for Windows
2. Add to system PATH
3. Install cairosvg: `pip install cairosvg pillow`

**Linux:**
```bash
sudo apt-get install libcairo2-dev
pip install cairosvg pillow
```

**macOS:**
```bash
brew install cairo
pip install cairosvg pillow
```

## Testing

### Run All Tests
```bash
python tests/test_visual_genetics_integration.py
```

### Run Individual Tests
```bash
python -c "from tests.test_visual_genetics_integration import test_visual_genetics; test_visual_genetics()"
```

### Performance Testing
```bash
python -c "from tests.test_visual_genetics_integration import test_performance; test_performance()"
```

## Integration with Main Game

### Basic Integration
```python
from core.visual_genetics import VisualGenetics
from core.turtle_svg_generator import TurtleSVGGenerator
from core.svg_pygame_renderer_simple import get_svg_renderer

# Initialize systems
vg = VisualGenetics()
generator = TurtleSVGGenerator()
renderer = get_svg_renderer()

# Generate turtle
genetics = vg.generate_random_genetics()
surface = renderer.render_turtle_to_surface(genetics, size=100)
```

### Full Voting System
```python
from core.voting_system import VotingSystem
from core.genetic_pool_manager import GeneticPoolManager

# Initialize voting
voting = VotingSystem()
pool_manager = GeneticPoolManager()
voting.set_genetic_pool_manager(pool_manager)

# Generate daily designs
designs = voting.generate_daily_designs()
```

## File Structure

```
TurboShells/
├── core/
│   ├── visual_genetics.py
│   ├── genetic_svg_mapper.py
│   ├── turtle_svg_generator.py
│   ├── pattern_generators.py
│   ├── svg_pygame_renderer_simple.py
│   ├── voting_system.py
│   └── genetic_pool_manager.py
├── ui/
│   └── voting_view.py
├── tests/
│   └── test_visual_genetics_integration.py
├── demo_visual_genetics.py
├── requirements_visual_genetics.txt
└── INSTALLATION_GUIDE.md
```

## Support

If you encounter issues:

1. Check the integration tests are passing
2. Verify all dependencies are installed
3. Run the demo to test basic functionality
4. Check this guide for common solutions

The system is designed to work with fallback options when optional dependencies are not available.
