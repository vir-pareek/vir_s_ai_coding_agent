import subprocess
import os
import time
import resource
import traceback
from typing import Tuple, Dict, Optional


class CodeExecutor:
    """Utility to execute Python code with given input, with enhanced runtime feedback."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def execute(self, code_file: str, input_file: str, output_file: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Execute Python code with input from file and save output to file.
        
        Enhanced with runtime metrics: execution time, memory usage, and stack traces.

        Args:
            code_file: Path to Python file to execute
            input_file: Path to input file
            output_file: Path to save output

        Returns:
            Tuple of (success: bool, error_message: str, metrics: Dict)
            metrics contains: execution_time, memory_usage, stack_trace (if error)
        """
        metrics = {
            'execution_time': None,
            'memory_usage_mb': None,
            'stack_trace': None,
            'return_code': None
        }
        
        if not os.path.exists(code_file):
            return False, f"Code file not found: {code_file}", metrics

        if not os.path.exists(input_file):
            return False, f"Input file not found: {input_file}", metrics

        try:
            with open(input_file, 'r') as f_in:
                input_data = f_in.read()

            # Measure execution time
            start_time = time.time()
            
            # Use psutil if available for accurate subprocess memory measurement
            # Otherwise, use resource which measures parent process (less accurate)
            try:
                import psutil
                use_psutil = True
            except ImportError:
                use_psutil = False
            
            if use_psutil:
                # More accurate: measure child process memory
                process = psutil.Popen(
                    ['python', code_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                try:
                    stdout, stderr = process.communicate(input=input_data, timeout=self.timeout)
                    end_time = time.time()
                    
                    # Get memory usage from process
                    try:
                        memory_info = process.memory_info()
                        memory_usage = memory_info.rss / (1024 * 1024)  # Convert bytes to MB
                    except:
                        memory_usage = None
                    
                    result = subprocess.CompletedProcess(
                        process.args,
                        process.returncode,
                        stdout,
                        stderr
                    )
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    raise subprocess.TimeoutExpired(process.args, self.timeout)
            else:
                # Fallback: use subprocess.run (memory measurement will be less accurate)
                result = subprocess.run(
                    ['python', code_file],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                end_time = time.time()
                # Memory measurement not available without psutil
                memory_usage = None
            
            execution_time = end_time - start_time
            
            metrics['execution_time'] = execution_time
            metrics['memory_usage_mb'] = memory_usage
            metrics['return_code'] = result.returncode

            if result.returncode != 0:
                # Extract stack trace from stderr if available
                stack_trace = self._extract_stack_trace(result.stderr)
                metrics['stack_trace'] = stack_trace
                
                error_msg = f"Execution failed with return code {result.returncode}\n"
                error_msg += f"Execution time: {execution_time:.3f}s\n"
                if memory_usage:
                    error_msg += f"Memory usage: {memory_usage:.2f} MB\n"
                error_msg += f"STDERR: {result.stderr}\n"
                error_msg += f"STDOUT: {result.stdout}"
                
                if stack_trace:
                    error_msg += f"\n\nStack Trace:\n{stack_trace}"
                
                return False, error_msg, metrics

            # Save output
            with open(output_file, 'w') as f_out:
                f_out.write(result.stdout)

            return True, "", metrics

        except subprocess.TimeoutExpired:
            metrics['execution_time'] = self.timeout
            return False, f"Execution timed out after {self.timeout} seconds", metrics
        except Exception as e:
            metrics['stack_trace'] = traceback.format_exc()
            return False, f"Execution error: {str(e)}\n{traceback.format_exc()}", metrics
    
    def _get_memory_usage(self) -> Optional[float]:
        """
        Get current memory usage in MB.
        
        NOTE: This measures the parent process memory, not the subprocess.
        For accurate subprocess memory measurement, use psutil (see execute method).
        """
        try:
            # Linux/Mac memory usage
            mem_info = resource.getrusage(resource.RUSAGE_SELF)
            # ru_maxrss is in KB on Linux, bytes on Mac
            # On Mac, divide by 1024 to get KB, then convert to MB
            if hasattr(mem_info, 'ru_maxrss'):
                # Mac returns bytes, Linux returns KB
                # Check if it's likely bytes (large number) or KB
                rss = mem_info.ru_maxrss
                if rss > 1000000:  # Likely bytes
                    return rss / (1024 * 1024)  # Convert bytes to MB
                else:
                    return rss / 1024  # Convert KB to MB
        except:
            pass
        return None
    
    def _extract_stack_trace(self, stderr: str) -> Optional[str]:
        """Extract stack trace from error output."""
        if not stderr:
            return None
        
        # Look for Traceback pattern
        if "Traceback" in stderr:
            lines = stderr.split('\n')
            traceback_start = None
            for i, line in enumerate(lines):
                if "Traceback" in line:
                    traceback_start = i
                    break
            
            if traceback_start is not None:
                # Extract stack trace (usually 5-20 lines)
                traceback_lines = lines[traceback_start:traceback_start + 20]
                return '\n'.join(traceback_lines)
        
        return None
