import os
import yaml
import json
import time
from typing import Dict, Optional, Tuple, List
from agents import TesterAgent, BruteAgent, OptimalAgent, WebSearchAgent
from utils import CodeExecutor, OutputComparator, ProgressIndicator, analyze_problem


class ProblemSolverOrchestrator:
    """Main orchestrator for the multi-agent problem solving system."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize orchestrator with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Set up API key
        api_keys = self.config.get('api_keys', {})

        # Google API key for Gemini
        google_key = api_keys.get('google')
        if google_key and google_key != "your-google-api-key-here":
            os.environ['GOOGLE_API_KEY'] = google_key

        # Initialize agents
        self.tester_agent = TesterAgent(self.config['models']['tester_agent'])
        # Get num_candidates from config (default 3)
        num_candidates = self.config.get('execution', {}).get('num_brute_candidates', 3)
        self.brute_agent = BruteAgent(self.config['models']['brute_agent'], num_candidates=num_candidates)
        self.optimal_agent = OptimalAgent(self.config['models']['optimal_agent'], num_candidates=num_candidates)
        
        # Get model selection strategy from config
        self.model_selection_strategy = self.config.get('model_selection', {}).get('strategy', 'static')
        self.difficulty_models = self.config.get('model_selection', {}).get('difficulty_models', {})
        
        # Initialize WebSearchAgent if configured
        if 'web_search_agent' in self.config['models']:
            self.web_search_agent = WebSearchAgent(self.config['models']['web_search_agent'])
        else:
            self.web_search_agent = None

        # Initialize utilities
        timeout = self.config['execution']['timeout_seconds']
        self.executor = CodeExecutor(timeout=timeout)
        self.comparator = OutputComparator()

        # Set up workspace
        self.workspace = self.config['output']['workspace_dir']
        os.makedirs(self.workspace, exist_ok=True)

        # File paths
        self.files = {
            'test_inputs': os.path.join(self.workspace, self.config['files']['test_inputs']),
            'brute_solution': os.path.join(self.workspace, self.config['files']['brute_solution']),
            'brute_outputs': os.path.join(self.workspace, self.config['files']['brute_outputs']),
            'optimal_solution': os.path.join(self.workspace, self.config['files']['optimal_solution']),
            'optimal_outputs': os.path.join(self.workspace, self.config['files']['optimal_outputs'])
        }

        self.max_attempts = self.config['execution']['max_optimal_attempts']

    def solve(self, problem_statement: str) -> Tuple[bool, Optional[str], Dict]:
        """
        Solve the given problem using multi-agent approach.

        Args:
            problem_statement: The problem description

        Returns:
            Tuple of (success, optimal_code, metadata)
        """
        metadata = {
            'attempts': 0,
            'test_cases_generated': False,
            'brute_force_generated': False,
            'brute_force_executed': False,
            'optimal_solution_found': False,
            'errors': [],
            'optimal_attempts': [],  # Store all attempts with details
            'problem_hints': None,
            'algorithm_type': 'General',
            'brute_attempts': [],  # Store all brute force attempts
            'problem_complexity': 'Easy',
            'recommended_approaches': []
        }
        
        # Analyze problem to extract hints and complexity targets
        print("=" * 80)
        print("STEP 0: Analyzing problem and extracting hints...")
        print("=" * 80)
        
        try:
            with ProgressIndicator("Analyzing problem statement"):
                problem_analysis = analyze_problem(problem_statement)
                metadata['problem_hints'] = problem_analysis['hints_summary']
                metadata['algorithm_type'] = problem_analysis['algorithm_type']
                metadata['recommended_approaches'] = problem_analysis.get('recommended_approaches', [])
                metadata['problem_complexity'] = problem_analysis.get('problem_complexity', 'Easy')
            
            # Optionally use WebSearchAgent to enhance hints
            if self.web_search_agent and metadata['problem_hints']:
                try:
                    with ProgressIndicator("Searching for algorithm approaches"):
                        web_search_results = self.web_search_agent.search_algorithm(problem_statement)
                        # Combine problem analysis with web search results
                        if web_search_results:
                            metadata['problem_hints'] += f"\n\nAdditional Algorithm Research:\n{web_search_results}"
                except Exception as e:
                    print(f"⚠ Web search failed: {str(e)} (continuing with basic hints)")
            
            if metadata['problem_hints']:
                print("\n✓ Problem analysis complete:")
                print(metadata['problem_hints'])
                if metadata['recommended_approaches']:
                    print(f"\n→ Will generate solutions using approaches: {', '.join(metadata['recommended_approaches'])}")
            print()
        except Exception as e:
            print(f"⚠ Problem analysis failed: {str(e)} (continuing without hints)\n")
            metadata['problem_hints'] = None

        print("=" * 80)
        print("STEP 1: Generating test cases...")
        print("=" * 80)

        try:
            with ProgressIndicator("Generating test cases with TesterAgent"):
                test_cases = self.tester_agent.generate_test_cases(problem_statement)
            with open(self.files['test_inputs'], 'w') as f:
                f.write(test_cases)
            metadata['test_cases_generated'] = True
            print(f"✓ Test cases saved to: {self.files['test_inputs']}\n")
        except Exception as e:
            error = f"Failed to generate test cases: {str(e)}"
            metadata['errors'].append(error)
            print(f"✗ {error}\n")
            return False, None, metadata

        print("=" * 80)
        print("STEP 2: Generating multiple brute force solutions...")
        print("=" * 80)

        try:
            with ProgressIndicator("Generating multiple brute force solution candidates"):
                # Generate multiple brute force solutions
                brute_candidates = self.brute_agent.generate_multiple_solutions(
                    problem_statement,
                    hints=metadata['problem_hints']
                )
                metadata['brute_force_generated'] = True
                print(f"✓ Generated {len(brute_candidates)} brute force solution candidates\n")
        except Exception as e:
            error = f"Failed to generate brute force solutions: {str(e)}"
            metadata['errors'].append(error)
            print(f"✗ {error}\n")
            return False, None, metadata

        print("=" * 80)
        print("STEP 3: Testing and selecting best brute force solution...")
        print("=" * 80)

        # Test each candidate and find the best one
        best_solution = None
        best_output = None
        best_solution_data = None

        for candidate in brute_candidates:
            attempt_num = candidate['number']
            print(f"\nTesting brute force solution {attempt_num}/{len(brute_candidates)}...")
            
            # Save this candidate to test
            candidate_file = os.path.join(self.workspace, f'brute_candidate_{attempt_num}.py')
            with open(candidate_file, 'w') as f:
                f.write(candidate['code'])
            
            # Execute this candidate
            output_file = os.path.join(self.workspace, f'brute_candidate_{attempt_num}_output.txt')
            success, error = self.executor.execute(
                candidate_file,
                self.files['test_inputs'],
                output_file
            )
            
            candidate_result = {
                'number': attempt_num,
                'code': candidate['code'],
                'execution_success': success,
                'error': error
            }
            
            if success:
                candidate_result['has_output'] = True
                candidate_result['selected'] = False
                print(f"✓ Solution {attempt_num} executed successfully")
                
                # If this is the first working solution, or we need the best one
                if best_solution is None:
                    best_solution = candidate['code']
                    best_output = output_file
                    best_solution_data = candidate_result
                    best_solution_data['selected'] = True
                    print(f"→ Solution {attempt_num} selected as best so far")
            else:
                candidate_result['has_output'] = False
                candidate_result['selected'] = False
                print(f"✗ Solution {attempt_num} execution failed: {error}")
            
            metadata['brute_attempts'].append(candidate_result)
        
        if not best_solution:
            error_msg = f"All {len(brute_candidates)} brute force solutions failed execution"
            metadata['errors'].append(error_msg)
            print(f"\n✗ {error_msg}\n")
            return False, None, metadata
        
        # Save the best solution as the official brute force solution
        with open(self.files['brute_solution'], 'w') as f:
            f.write(best_solution)
        
        # Copy the best output
        if os.path.exists(best_output):
            with open(best_output, 'r') as f_in:
                with open(self.files['brute_outputs'], 'w') as f_out:
                    f_out.write(f_in.read())
        
        metadata['brute_force_executed'] = True
        print(f"\n✓ Selected best brute force solution (from {len(brute_candidates)} candidates)")
        print(f"✓ Brute force solution saved to: {self.files['brute_solution']}")
        print(f"✓ Brute force outputs saved to: {self.files['brute_outputs']}\n")

        print("=" * 80)
        print("STEP 4: Generating and testing optimal solution...")
        print("=" * 80)

        feedback = None
        optimal_code = None
        
        # Determine if we should use parallel generation
        use_parallel = len(metadata.get('recommended_approaches', [])) > 1
        
        # Try parallel generation first if we have multiple approaches
        if use_parallel:
            approaches = metadata['recommended_approaches']
            print(f"\n→ Generating {len(approaches)} solutions in parallel using different approaches...")
            
            try:
                with ProgressIndicator(f"Generating parallel solutions with approaches: {', '.join(approaches)}"):
                    parallel_solutions = self.optimal_agent.generate_parallel_solutions(
                        problem_statement,
                        approaches=approaches,
                        hints=metadata['problem_hints']
                    )
                
                print(f"✓ Generated {len(parallel_solutions)} parallel solutions\n")
                
                # Test each parallel solution and pick the best one
                best_parallel_solution = None
                best_parallel_approach = None
                
                for solution in parallel_solutions:
                    approach = solution.get('approach', 'Unknown')
                    code = solution.get('code', '')
                    
                    if not code:
                        print(f"✗ {approach} solution failed to generate")
                        continue
                    
                    # Test this solution
                    approach_file = os.path.join(self.workspace, f'optimal_approach_{approach.replace(" ", "_")}.py')
                    with open(approach_file, 'w') as f:
                        f.write(code)
                    
                    approach_output = os.path.join(self.workspace, f'optimal_approach_{approach.replace(" ", "_")}_output.txt')
                    success, error = self.executor.execute(
                        approach_file,
                        self.files['test_inputs'],
                        approach_output
                    )
                    
                    if success:
                        print(f"✓ {approach} solution executed successfully")
                        
                        # Check if outputs match
                        if self.comparator.compare(self.files['brute_outputs'], approach_output):
                            print(f"✓ {approach} solution outputs MATCH!")
                            best_parallel_solution = code
                            best_parallel_approach = approach
                            metadata['optimal_solution_found'] = True
                            metadata['optimal_attempts'].append({
                                'attempt_number': 0,
                                'approach': approach,
                                'verdict': 'Accepted',
                                'output_match': True
                            })
                            break
                    else:
                        print(f"✗ {approach} solution execution failed: {error}")
                
                if best_parallel_solution:
                    print(f"\n✓ Parallel generation succeeded! Best approach: {best_parallel_approach}")
                    optimal_code = best_parallel_solution
                    
                    # Save as the final solution
                    with open(self.files['optimal_solution'], 'w') as f:
                        f.write(optimal_code)
                    
                    # Generate results JSON
                    self._generate_results_json(problem_statement, metadata)
                    
                    return True, optimal_code, metadata
                else:
                    print("\n⚠ Parallel solutions didn't pass, falling back to sequential attempts...\n")
            
            except Exception as e:
                print(f"⚠ Parallel generation failed: {str(e)} (falling back to sequential)\n")

        for attempt in range(1, self.max_attempts + 1):
            metadata['attempts'] = attempt
            print(f"\n--- Attempt {attempt}/{self.max_attempts} ---")

            attempt_data = {
                'attempt_number': attempt,
                'timestamp': time.time(),
                'code': None,
                'verdict': None,
                'error_message': None,
                'execution_success': False,
                'output_match': False,
                'output_diff': None
            }

            try:
                with ProgressIndicator(f"Generating optimal solution (attempt {attempt}/{self.max_attempts})"):
                    optimal_code = self.optimal_agent.generate_solution(
                        problem_statement,
                        feedback=feedback,
                        attempt=attempt,
                        hints=metadata['problem_hints']
                    )

                attempt_data['code'] = optimal_code

                # Save this attempt separately
                attempt_file = os.path.join(self.workspace, f'optimal_attempt_{attempt}.py')
                with open(attempt_file, 'w') as f:
                    f.write(optimal_code)

                # Also update the main optimal solution file
                with open(self.files['optimal_solution'], 'w') as f:
                    f.write(optimal_code)

                print(f"✓ Generated optimal solution")

            except Exception as e:
                error = f"Failed to generate optimal solution: {str(e)}"
                attempt_data['verdict'] = 'Generation Failed'
                attempt_data['error_message'] = str(e)
                metadata['errors'].append(error)
                metadata['optimal_attempts'].append(attempt_data)
                print(f"✗ {error}")
                continue

            # Execute optimal solution
            attempt_output_file = os.path.join(self.workspace, f'optimal_attempt_{attempt}_output.txt')
            success, error = self.executor.execute(
                self.files['optimal_solution'],
                self.files['test_inputs'],
                attempt_output_file
            )

            # Also update main output file
            if success:
                with open(self.files['optimal_outputs'], 'w') as f_out:
                    with open(attempt_output_file, 'r') as f_in:
                        f_out.write(f_in.read())

            if not success:
                print(f"✗ Execution failed: {error}")
                attempt_data['verdict'] = 'Runtime Error'
                attempt_data['error_message'] = error
                attempt_data['execution_success'] = False
                metadata['optimal_attempts'].append(attempt_data)
                feedback = f"Your solution failed to execute:\n{error}\n\nPlease fix the errors."
                metadata['errors'].append(f"Attempt {attempt}: Execution failed - {error}")
                continue

            attempt_data['execution_success'] = True
            print(f"✓ Execution successful")

            # Compare outputs
            if self.comparator.compare(self.files['brute_outputs'], attempt_output_file):
                print(f"✓ Outputs match! Solution found in {attempt} attempt(s)")
                attempt_data['verdict'] = 'Accepted'
                attempt_data['output_match'] = True
                metadata['optimal_attempts'].append(attempt_data)
                metadata['optimal_solution_found'] = True
                print("\n" + "=" * 80)
                print("SUCCESS: Optimal solution found!")
                print("=" * 80)

                # Generate results JSON for viewer
                self._generate_results_json(problem_statement, metadata)

                return True, optimal_code, metadata
            else:
                diff = self.comparator.get_diff_summary(
                    self.files['brute_outputs'],
                    attempt_output_file
                )
                print(f"✗ Outputs don't match")
                print(f"Difference: {diff[:200]}...")
                attempt_data['verdict'] = 'Wrong Answer'
                attempt_data['output_match'] = False
                attempt_data['output_diff'] = diff
                metadata['optimal_attempts'].append(attempt_data)
                feedback = f"Your solution produced incorrect output:\n{diff}\n\nPlease fix the logic."
                metadata['errors'].append(f"Attempt {attempt}: Output mismatch")

        print("\n" + "=" * 80)
        print(f"FAILED: Could not find correct solution in {self.max_attempts} attempts")
        print("=" * 80)

        # Generate results JSON even on failure
        self._generate_results_json(problem_statement, metadata)

        return False, optimal_code, metadata

    def _generate_results_json(self, problem_statement: str, metadata: Dict):
        """Generate results.json for the web viewer."""
        # Read all necessary files
        test_input = ""
        brute_code = ""
        brute_output = ""

        try:
            with open(self.files['test_inputs'], 'r') as f:
                test_input = f.read()
        except:
            pass

        try:
            with open(self.files['brute_solution'], 'r') as f:
                brute_code = f.read()
        except:
            pass

        try:
            with open(self.files['brute_outputs'], 'r') as f:
                brute_output = f.read()
        except:
            pass

        results = {
            'problem_statement': problem_statement,
            'test_input': test_input,
            'test_output': brute_output,
            'brute_force_code': brute_code,
            'brute_attempts': metadata.get('brute_attempts', []),
            'optimal_attempts': metadata['optimal_attempts'],
            'success': metadata['optimal_solution_found'],
            'total_attempts': metadata['attempts']
        }

        results_file = os.path.join(self.workspace, 'results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to: {results_file}")
        print("\n" + "=" * 80)
        print("📊 VIEW RESULTS IN WEB BROWSER")
        print("=" * 80)
        print("\nTo view the beautiful HTML report, run:")
        print("\n  python -m http.server 8000")
        print("\nThen open: http://localhost:8000/viewer.html")
        print("\n(HTTP server needed to avoid CORS restrictions)")
        print("=" * 80)
