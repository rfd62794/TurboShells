
import pytest
import sys
import io

# Redirect stdout to capture output
stdout_capture = io.StringIO()
stderr_capture = io.StringIO()

original_stdout = sys.stdout
original_stderr = sys.stderr

sys.stdout = stdout_capture
sys.stderr = stderr_capture

print("Starting tests...")
retcode = pytest.main(["tests/test_persistence_layer.py", "tests/test_api_roster.py", "-v", "-s", "--color=no"])
print(f"Tests finished with exit code: {retcode}")

sys.stdout = original_stdout
sys.stderr = original_stderr

print("STDOUT CAPTURE:")
print(stdout_capture.getvalue())
print("\nSTDERR CAPTURE:")
print(stderr_capture.getvalue())
