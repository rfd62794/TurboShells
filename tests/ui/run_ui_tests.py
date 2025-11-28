"""
UI Test Runner

Organized test runner for all UI-related tests including:
- Component tests
- Panel tests  
- Integration tests
- Performance tests
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


class UITestRunner:
    """Organized test runner for UI tests."""
    
    def __init__(self):
        self.test_categories = {
            'components': 'tests/ui/components',
            'panels': 'tests/ui/panels', 
            'integration': 'tests/ui/integration',
            'all': 'tests/ui'
        }
        
    def run_tests(self, category='all', verbose=False, coverage=False, specific_test=None):
        """Run tests for specified category."""
        if specific_test:
            return self._run_specific_test(specific_test, verbose, coverage)
            
        if category not in self.test_categories:
            print(f"❌ Unknown test category: {category}")
            print(f"Available categories: {list(self.test_categories.keys())}")
            return False
            
        test_path = self.test_categories[category]
        return self._run_pytest(test_path, verbose, coverage)
    
    def _run_specific_test(self, test_file, verbose, coverage):
        """Run a specific test file."""
        if not test_file.endswith('.py'):
            test_file += '.py'
            
        # Find the test file
        for category, path in self.test_categories.items():
            if category == 'all':
                continue
            full_path = Path(path) / test_file
            if full_path.exists():
                return self._run_pytest(str(full_path), verbose, coverage)
        
        print(f"❌ Test file not found: {test_file}")
        return False
    
    def _run_pytest(self, test_path, verbose, coverage):
        """Run pytest with specified options."""
        cmd = ['python', '-m', 'pytest', test_path]
        
        if verbose:
            cmd.append('-v')
        else:
            cmd.append('-q')
            
        if coverage:
            cmd.extend(['--cov=src/ui', '--cov-report=term-missing'])
        
        # Add pytest configuration
        cmd.extend(['--tb=short', '--strict-markers'])
        
        print(f"🧪 Running UI tests: {' '.join(cmd)}")
        print("="*60)
        
        try:
            result = subprocess.run(cmd, cwd=project_root, capture_output=False)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def run_component_tests(self, verbose=False, coverage=False):
        """Run component tests only."""
        return self.run_tests('components', verbose, coverage)
    
    def run_panel_tests(self, verbose=False, coverage=False):
        """Run panel tests only."""
        return self.run_tests('panels', verbose, coverage)
    
    def run_integration_tests(self, verbose=False, coverage=False):
        """Run integration tests only."""
        return self.run_tests('integration', verbose, coverage)
    
    def run_all_ui_tests(self, verbose=False, coverage=False):
        """Run all UI tests."""
        return self.run_tests('all', verbose, coverage)
    
    def list_tests(self):
        """List all available test files."""
        print("📋 Available UI Test Files:")
        print("="*50)
        
        for category, path in self.test_categories.items():
            if category == 'all':
                continue
                
            print(f"\n📁 {category.upper()}:")
            test_path = Path(path)
            if test_path.exists():
                for test_file in test_path.glob('test_*.py'):
                    print(f"  - {test_file.name}")
            else:
                print(f"  (directory not found: {path})")
    
    def run_quick_tests(self):
        """Run a quick subset of important tests."""
        quick_tests = [
            'tests/ui/panels/test_main_menu_refactored.py::TestMainMenuRefactored::test_initialization',
            'tests/ui/panels/test_main_menu_refactored.py::TestMainMenuRefactored::test_component_creation', 
            'tests/ui/components/test_reusable_components.py::TestButtonComponent::test_button_initialization',
            'tests/ui/components/test_reusable_components.py::TestMoneyDisplayComponent::test_money_display_initialization'
        ]
        
        cmd = ['python', '-m', 'pytest'] + quick_tests + ['-v']
        
        print("🚀 Running Quick UI Tests...")
        print("="*50)
        
        try:
            result = subprocess.run(cmd, cwd=project_root, capture_output=False)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error running quick tests: {e}")
            return False


def main():
    """Main entry point for UI test runner."""
    parser = argparse.ArgumentParser(description='UI Test Runner for TurboShells')
    parser.add_argument('category', nargs='?', default='all',
                       help='Test category to run (components, panels, integration, all)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-c', '--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('-t', '--test', 
                       help='Run specific test file')
    parser.add_argument('-l', '--list', action='store_true',
                       help='List all available test files')
    parser.add_argument('-q', '--quick', action='store_true',
                       help='Run quick tests only')
    
    args = parser.parse_args()
    
    runner = UITestRunner()
    
    if args.list:
        runner.list_tests()
        return 0
    
    if args.quick:
        success = runner.run_quick_tests()
    elif args.test:
        success = runner.run_tests(specific_test=args.test, verbose=args.verbose, coverage=args.coverage)
    else:
        success = runner.run_tests(args.category, args.verbose, args.coverage)
    
    if success:
        print("\n🎉 UI Tests Completed Successfully!")
        return 0
    else:
        print("\n❌ UI Tests Failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
