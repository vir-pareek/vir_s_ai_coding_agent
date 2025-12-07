import os
import yaml
import json
import time
from typing import Dict, Optional, Tuple, List
from agents import TesterAgent, BruteAgent, OptimalAgent, WebSearchAgent, DebugAgent, ValidatorAgent, ComplexityAgent, SolutionSelectorAgent
from utils import CodeExecutor, OutputComparator, ProgressIndicator, analyze_problem
from utils.api_utils import retry_with_backoff


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

        # Get model selection strategy from config
        self.model_selection_strategy = self.config.get('model_selection', {}).get('strategy', 'static')
        self.difficulty_models = self.config.get('model_selection', {}).get('difficulty_models', {})
        
        # Initialize agents with potential adaptive model selection
        # (Will be updated after problem analysis if strategy is 'adaptive')
        tester_model = self.config['models']['tester_agent']
        brute_model = self.config['models']['brute_agent']
        self.optimal_model = self.config['models']['optimal_agent']  # Store as instance variable
        
        self.tester_agent = TesterAgent(tester_model)
        # Get num_candidates from config (default 3)
        self.num_candidates = self.config.get('execution', {}).get('num_brute_candidates', 3)  # Store as instance variable
        self.brute_agent = BruteAgent(brute_model, num_candidates=self.num_candidates)
        self.optimal_agent = OptimalAgent(self.optimal_model, num_candidates=self.num_candidates)
        
        # Initialize WebSearchAgent if configured
        if 'web_search_agent' in self.config['models']:
            self.web_search_agent = WebSearchAgent(self.config['models']['web_search_agent'])
        else:
            self.web_search_agent = None
        
        # Initialize specialized agents if configured
        if 'debug_agent' in self.config.get('models', {}):
            self.debug_agent = DebugAgent(self.config['models']['debug_agent'])
        else:
            self.debug_agent = None
        
        if 'validator_agent' in self.config.get('models', {}):
            self.validator_agent = ValidatorAgent(self.config['models']['validator_agent'])
        else:
            self.validator_agent = None
        
        if 'complexity_agent' in self.config.get('models', {}):
            self.complexity_agent = ComplexityAgent(self.config['models']['complexity_agent'])
        else:
            self.complexity_agent = None
        
        # Initialize solution selector agent
        if 'optimal_agent' in self.config.get('models', {}):
            selector_model = self.config['models']['optimal_agent']  # Use same model as optimal agent
            self.solution_selector = SolutionSelectorAgent(selector_model, self.complexity_agent)
        else:
            self.solution_selector = None

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
        
        # Store problem_analysis as instance variable for later use
        problem_analysis = None
        try:
            with ProgressIndicator("Analyzing problem statement"):
                problem_analysis = analyze_problem(problem_statement)
                self.problem_analysis = problem_analysis  # Store as instance variable
                metadata['problem_hints'] = problem_analysis['hints_summary']
                metadata['algorithm_type'] = problem_analysis['algorithm_type']
                metadata['recommended_approaches'] = problem_analysis.get('recommended_approaches', [])
                metadata['problem_complexity'] = problem_analysis.get('problem_complexity', 'Easy')
            
            # Adaptive model selection based on problem difficulty
            if self.model_selection_strategy == 'adaptive' and self.difficulty_models:
                problem_complexity = metadata.get('problem_complexity', 'Easy')
                selected_model = self.difficulty_models.get(problem_complexity, self.config['models']['optimal_agent'])
                
                if selected_model != self.optimal_model:
                    print(f"→ Adaptive model selection: Using {selected_model} for {problem_complexity} problem")
                    # Re-initialize optimal agent with selected model
                    self.optimal_agent = OptimalAgent(selected_model, num_candidates=self.num_candidates)
            
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
            self.problem_analysis = None  # Initialize to None if analysis failed

        print("=" * 80)
        print("STEP 1: Generating test cases...")
        print("=" * 80)

        try:
            with ProgressIndicator("Generating test cases with TesterAgent"):
                test_cases = self.tester_agent.generate_test_cases(problem_statement)
            
            # Generate STRESS TEST if problem is Hard/Competition
            if metadata.get('problem_complexity') in ['Hard', 'Competition']:
                print("→ Generating STRESS TEST case due to high difficulty...")
                try:
                    stress_test = self.tester_agent.generate_stress_test(problem_statement)
                    if stress_test:
                        test_cases += "\n" + stress_test
                        print("✓ Stress test added")
                except Exception as e:
                    print(f"⚠ Stress test generation failed: {e}")

            # Clean up test cases: remove blank lines between test cases
            lines = test_cases.split('\n')
            filtered_lines = []
            prev_was_empty = False
            for line in lines:
                if line.strip():  # Non-empty line
                    filtered_lines.append(line)
                    prev_was_empty = False
                elif not prev_was_empty and filtered_lines:  # First blank line after non-empty
                    # Only keep if it's the first line (T header) or if it helps readability
                    # Actually, better to remove all blank lines for consistent parsing
                    prev_was_empty = True
            
            # Remove all blank lines to ensure clean input parsing
            cleaned_test_cases = '\n'.join([l for l in lines if l.strip()])
            
            with open(self.files['test_inputs'], 'w') as f:
                f.write(cleaned_test_cases)
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
            success, error, metrics = self.executor.execute(
                candidate_file,
                self.files['test_inputs'],
                output_file
            )
            
            candidate_result = {
                'number': attempt_num,
                'code': candidate['code'],
                'execution_success': success,
                'error': error,
                'execution_time': metrics.get('execution_time'),
                'memory_usage_mb': metrics.get('memory_usage_mb')
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
        print("STEP 4: Generating multiple optimal solutions with different temperatures...")
        print("=" * 80)

        feedback = None
        optimal_code = None
        
        # Get configuration for multi-temperature generation
        num_optimal_candidates = self.config.get('execution', {}).get('num_optimal_candidates', 10)
        temp_low = self.config.get('execution', {}).get('temperature_low', 0.1)
        temp_high = self.config.get('execution', {}).get('temperature_high', 0.3)
        
        # Generate solutions with different temperatures (reduced for quota management)
        num_low = num_optimal_candidates // 2
        num_high = num_optimal_candidates - num_low
        print(f"\n→ Generating {num_optimal_candidates} solutions ({num_low} at temp={temp_low}, {num_high} at temp={temp_high})...")
        
        try:
            with ProgressIndicator(f"Generating {num_optimal_candidates} solution candidates"):
                multi_temp_solutions = self.optimal_agent.generate_multiple_temperature_solutions(
                    problem_statement,
                    num_solutions=num_optimal_candidates,
                    temp_low=temp_low,
                    temp_high=temp_high,
                    hints=metadata['problem_hints']
                )
            
            print(f"✓ Generated {len(multi_temp_solutions)} solution candidates\n")
            
            # Filter valid solutions
            valid_solutions = [s for s in multi_temp_solutions if s.get('code') and not s.get('error')]
            print(f"✓ {len(valid_solutions)} valid solutions (out of {len(multi_temp_solutions)} generated)\n")
            
            if not valid_solutions:
                print("✗ No valid solutions generated, falling back to single solution generation...\n")
            else:
                # Use solution selector to pick the best one
                print("→ Analyzing solutions and selecting the best one...")
                
                # Get constraints for complexity checking
                constraints = {}
                if hasattr(self, 'problem_analysis') and self.problem_analysis:
                    constraints = self.problem_analysis.get('key_constraints', {})
                
                if self.solution_selector:
                    selection_result = self.solution_selector.select_best_solution(
                        valid_solutions,
                        problem_statement,
                        constraints
                    )
                    
                    selected_solution = selection_result.get('selected_solution')
                    selected_number = selection_result.get('selected_number')
                    reason = selection_result.get('reason', '')
                    complexity_check = selection_result.get('complexity_check')
                    
                    if selected_solution:
                        print(f"✓ Selected Solution #{selected_number} (temp={selected_solution.get('temperature', 'N/A')})")
                        print(f"  Reason: {reason[:200]}")
                        if complexity_check:
                            print(f"  Complexity: {complexity_check.get('time_complexity', 'Unknown')}")
                            if complexity_check.get('meets_constraints') is False:
                                print(f"  ⚠ TLE RISK: {complexity_check.get('reason', 'Complexity too high')}")
                        
                        # Test the selected solution
                        selected_code = selected_solution.get('code', '')
                        if selected_code:
                            test_file = os.path.join(self.workspace, f'optimal_selected_{selected_number}.py')
                            with open(test_file, 'w') as f:
                                f.write(selected_code)
                            
                            test_output = os.path.join(self.workspace, f'optimal_selected_{selected_number}_output.txt')
                            success, error, metrics = self.executor.execute(
                                test_file,
                                self.files['test_inputs'],
                                test_output
                            )
                            
                            if success:
                                print(f"✓ Selected solution executed successfully")
                                
                                # Check if outputs match
                                if self.comparator.compare(self.files['brute_outputs'], test_output):
                                    print(f"✓ Selected solution outputs MATCH!")
                                    optimal_code = selected_code
                                    metadata['optimal_solution_found'] = True
                                    metadata['optimal_attempts'].append({
                                        'attempt_number': 0,
                                        'approach': f'Multi-temp selection (temp={selected_solution.get("temperature")})',
                                        'verdict': 'Accepted',
                                        'output_match': True,
                                        'selection_reason': reason
                                    })
                                    
                                    # Save the correct solution
                                    with open(self.files['optimal_solution'], 'w') as f:
                                        f.write(optimal_code)
                                    print(f"✓ Correct solution saved to: {self.files['optimal_solution']}")
                                    
                                    # Save output
                                    with open(self.files['optimal_outputs'], 'w') as f_out:
                                        with open(test_output, 'r') as f_in:
                                            f_out.write(f_in.read())
                                    print(f"✓ Correct output saved to: {self.files['optimal_outputs']}")
                                    
                                    self._generate_results_json(problem_statement, metadata)
                                    return True, optimal_code, metadata
                                else:
                                    print(f"✗ Selected solution outputs don't match, will try other solutions...")
                            else:
                                print(f"✗ Selected solution execution failed: {error}")
                
                # If selection didn't work, test all valid solutions
                print("\n→ Testing all valid solutions to find a working one...")
                for solution in valid_solutions:
                    code = solution.get('code', '')
                    number = solution.get('number', 0)
                    temp = solution.get('temperature', 0.0)
                    
                    if not code:
                        continue
                    
                    test_file = os.path.join(self.workspace, f'optimal_candidate_{number}.py')
                    with open(test_file, 'w') as f:
                        f.write(code)
                    
                    test_output = os.path.join(self.workspace, f'optimal_candidate_{number}_output.txt')
                    success, error, metrics = self.executor.execute(
                        test_file,
                        self.files['test_inputs'],
                        test_output
                    )
                    
                    if success:
                        if self.comparator.compare(self.files['brute_outputs'], test_output):
                            print(f"✓ Solution #{number} (temp={temp}) outputs MATCH!")
                            optimal_code = code
                            metadata['optimal_solution_found'] = True
                            metadata['optimal_attempts'].append({
                                'attempt_number': 0,
                                'approach': f'Multi-temp candidate #{number} (temp={temp})',
                                'verdict': 'Accepted',
                                'output_match': True
                            })
                            
                            # Save the correct solution
                            with open(self.files['optimal_solution'], 'w') as f:
                                f.write(optimal_code)
                            print(f"✓ Correct solution saved to: {self.files['optimal_solution']}")
                            
                            # Save output
                            with open(self.files['optimal_outputs'], 'w') as f_out:
                                with open(test_output, 'r') as f_in:
                                    f_out.write(f_in.read())
                            print(f"✓ Correct output saved to: {self.files['optimal_outputs']}")
                            
                            self._generate_results_json(problem_statement, metadata)
                            return True, optimal_code, metadata
                        else:
                            print(f"✗ Solution #{number} outputs don't match")
                    else:
                        print(f"✗ Solution #{number} execution failed: {error[:100]}")
        
        except Exception as e:
            print(f"⚠ Multi-temperature generation failed: {str(e)} (falling back to standard generation)\n")
        
        # Fallback to standard generation if multi-temperature didn't work
        print("\n" + "=" * 80)
        print("STEP 4 (Fallback): Generating optimal solution...")
        print("=" * 80)
        
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
                    success, error, metrics = self.executor.execute(
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
                    
                    # CRITICAL: Save the CORRECT solution to optimal.py
                    with open(self.files['optimal_solution'], 'w') as f:
                        f.write(optimal_code)
                    print(f"✓ Correct solution saved to: {self.files['optimal_solution']}")
                    
                    # Save the correct output
                    approach_output = os.path.join(self.workspace, f'optimal_approach_{best_parallel_approach.replace(" ", "_")}_output.txt')
                    if os.path.exists(approach_output):
                        with open(self.files['optimal_outputs'], 'w') as f_out:
                            with open(approach_output, 'r') as f_in:
                                f_out.write(f_in.read())
                        print(f"✓ Correct output saved to: {self.files['optimal_outputs']}")
                    
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

                # Optional: Validate code before execution (if ValidatorAgent available)
                if self.validator_agent:
                    try:
                        print("→ Validating generated code...")
                        validation = self.validator_agent.validate_code(optimal_code, problem_statement)
                        attempt_data['validation'] = validation
                        
                        if not validation['valid']:
                            print(f"⚠ Validation failed: {', '.join(validation['issues'][:2])}")
                            # Refinement Loop: If validation fails, retry immediately
                            feedback = f"Pre-execution validation failed: {'; '.join(validation['issues'])}. Please fix these issues."
                            metadata['errors'].append(f"Attempt {attempt}: Validation failed")
                            continue # Skip execution and retry
                    except Exception as e:
                        print(f"⚠ Validation error: {e}")

                # Optional: Analyze complexity (if ComplexityAgent available)
                if self.complexity_agent:
                    try:
                        print("→ Analyzing time complexity...")
                        # Use stored problem_analysis or get from metadata
                        constraints = {}
                        if hasattr(self, 'problem_analysis') and self.problem_analysis:
                            constraints = self.problem_analysis.get('key_constraints', {})
                        elif 'problem_hints' in metadata and metadata['problem_hints']:
                            # Fallback: try to extract from metadata
                            constraints = metadata.get('key_constraints', {})
                        
                        complexity_analysis = self.complexity_agent.analyze_complexity(
                            optimal_code,
                            constraints
                        )
                        attempt_data['complexity_analysis'] = complexity_analysis
                        
                        if complexity_analysis.get('time_complexity'):
                            print(f"→ Estimated complexity: {complexity_analysis['time_complexity']}")
                        
                        # CRITICAL: If complexity is too high, REJECT immediately
                        if complexity_analysis.get('meets_constraints') is False:
                            error_msg = f"Complexity {complexity_analysis.get('time_complexity')} is too slow for constraints! Expected better."
                            print(f"✗ REJECTED: {error_msg}")
                            feedback = f"Your solution was rejected because the Time Complexity {complexity_analysis.get('time_complexity')} is too slow for the constraints. You MUST optimize it. {complexity_analysis.get('reason', '')}"
                            metadata['errors'].append(f"Attempt {attempt}: Rejected due to TLE risk")
                            continue  # Skip execution and retry
                            
                    except Exception as e:
                        print(f"⚠ Complexity analysis failed: {e}")

                # Save this attempt separately
                attempt_file = os.path.join(self.workspace, f'optimal_attempt_{attempt}.py')
                with open(attempt_file, 'w') as f:
                    f.write(optimal_code)

                # Also update the main optimal solution file
                with open(self.files['optimal_solution'], 'w') as f:
                    f.write(optimal_code)

                print(f"✓ Generated optimal solution")

            except ValueError as e:
                # Code extraction/validation failed - provide specific feedback
                error = f"Code generation validation failed: {str(e)}"
                attempt_data['verdict'] = 'Generation Failed'
                attempt_data['error_message'] = str(e)
                metadata['errors'].append(error)
                metadata['optimal_attempts'].append(attempt_data)
                print(f"✗ {error}")
                print(f"  → The generated code didn't pass validation. Retrying with more explicit instructions...")
                # Add feedback for next attempt
                feedback = f"Previous attempt failed code validation: {str(e)}\n\nCRITICAL: You must output ONLY valid Python code starting with 'import' statements. No markdown, no explanations, no text before the code. The code must be complete and runnable."
                continue
            except Exception as e:
                error = f"Failed to generate optimal solution: {str(e)}"
                attempt_data['verdict'] = 'Generation Failed'
                attempt_data['error_message'] = str(e)
                metadata['errors'].append(error)
                metadata['optimal_attempts'].append(attempt_data)
                print(f"✗ {error}")
                feedback = f"Generation failed with error: {str(e)}\n\nPlease ensure you output ONLY valid Python code, no markdown or explanations."
                continue

            # Execute optimal solution
            attempt_output_file = os.path.join(self.workspace, f'optimal_attempt_{attempt}_output.txt')
            success, error, metrics = self.executor.execute(
                self.files['optimal_solution'],
                self.files['test_inputs'],
                attempt_output_file
            )
            
            # Store metrics
            attempt_data['execution_time'] = metrics.get('execution_time')
            attempt_data['memory_usage_mb'] = metrics.get('memory_usage_mb')
            attempt_data['stack_trace'] = metrics.get('stack_trace')

            # Also update main output file
            if success:
                with open(self.files['optimal_outputs'], 'w') as f_out:
                    with open(attempt_output_file, 'r') as f_in:
                        f_out.write(f_in.read())

            if not success:
                exec_time_info = f" (took {metrics.get('execution_time', 0):.3f}s)" if metrics.get('execution_time') else ""
                print(f"✗ Execution failed{exec_time_info}: {error}")
                attempt_data['verdict'] = 'Runtime Error'
                attempt_data['error_message'] = error
                attempt_data['execution_success'] = False
                metadata['optimal_attempts'].append(attempt_data)
                
                # Enhanced feedback with runtime metrics
                feedback_parts = [f"Your solution failed to execute:\n{error}"]
                if metrics.get('execution_time'):
                    feedback_parts.append(f"Execution time: {metrics['execution_time']:.3f}s")
                if metrics.get('memory_usage_mb'):
                    feedback_parts.append(f"Memory usage: {metrics['memory_usage_mb']:.2f} MB")
                if metrics.get('stack_trace'):
                    feedback_parts.append(f"\nStack Trace:\n{metrics['stack_trace'][:500]}")
                
                # Use DebugAgent if available
                if self.debug_agent:
                    try:
                        debug_insights = self.debug_agent.analyze_failure(
                            optimal_code,
                            error,
                            metrics.get('stack_trace'),
                            metrics.get('execution_time'),
                            metrics.get('memory_usage_mb')
                        )
                        feedback_parts.append(f"\n=== Debugging Insights ===\n{debug_insights[:500]}")
                    except Exception as e:
                        pass  # Continue without debug insights if it fails
                
                feedback_parts.append("\nPlease fix the errors.")
                
                feedback = "\n".join(feedback_parts)
                metadata['errors'].append(f"Attempt {attempt}: Execution failed - {error}")
                continue

            attempt_data['execution_success'] = True
            exec_time_info = f" (took {metrics.get('execution_time', 0):.3f}s)" if metrics.get('execution_time') else ""
            mem_info = f", memory: {metrics.get('memory_usage_mb', 0):.2f} MB" if metrics.get('memory_usage_mb') else ""
            print(f"✓ Execution successful{exec_time_info}{mem_info}")

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

                # CRITICAL: Save the CORRECT solution to optimal.py
                with open(self.files['optimal_solution'], 'w') as f:
                    f.write(optimal_code)
                print(f"✓ Correct solution saved to: {self.files['optimal_solution']}")
                
                # Also save the correct output
                with open(self.files['optimal_outputs'], 'w') as f_out:
                    with open(attempt_output_file, 'r') as f_in:
                        f_out.write(f_in.read())
                print(f"✓ Correct output saved to: {self.files['optimal_outputs']}")

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
                
                # Enhanced feedback with debugging insights for wrong answers
                feedback_parts = [f"Your solution produced incorrect output:\n{diff[:1000]}"]
                
                # Use DebugAgent if available for wrong answers
                if self.debug_agent:
                    try:
                        debug_insights = self.debug_agent.analyze_failure(
                            optimal_code,
                            "Wrong Answer - output doesn't match expected",
                            output_diff=diff[:1000]
                        )
                        feedback_parts.append(f"\n=== Debugging Insights ===\n{debug_insights[:500]}")
                    except Exception as e:
                        pass  # Continue without debug insights if it fails
                
                feedback_parts.append("\nPlease fix the logic.")
                feedback = "\n".join(feedback_parts)
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
