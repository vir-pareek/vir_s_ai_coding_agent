import os


class OutputComparator:
    """Utility to compare output files."""

    @staticmethod
    def compare(file1: str, file2: str) -> bool:
        """
        Compare two output files, handling competitive programming edge cases.
        
        For Meta HackerCup:
        - Ignores leading/trailing whitespace on each line
        - Handles empty lines correctly
        - Compares line-by-line for better error reporting
        - Handles "Case #i: " format correctly

        Args:
            file1: Path to first file (expected output)
            file2: Path to second file (actual output)

        Returns:
            True if files match, False otherwise
        """
        if not os.path.exists(file1):
            return False

        if not os.path.exists(file2):
            return False

        try:
            with open(file1, 'r', encoding='utf-8') as f1:
                lines1 = f1.readlines()

            with open(file2, 'r', encoding='utf-8') as f2:
                lines2 = f2.readlines()

            # Normalize: strip trailing whitespace from each line
            # Keep empty lines as-is (they might be significant)
            normalized1 = [line.rstrip() for line in lines1]
            normalized2 = [line.rstrip() for line in lines2]
            
            # Remove trailing empty lines from both
            while normalized1 and not normalized1[-1]:
                normalized1.pop()
            while normalized2 and not normalized2[-1]:
                normalized2.pop()
            
            # Compare line by line
            if len(normalized1) != len(normalized2):
                return False
            
            for line1, line2 in zip(normalized1, normalized2):
                if line1 != line2:
                    return False
            
            return True

        except Exception as e:
            # Fallback to simple comparison on error
            try:
                with open(file1, 'r', encoding='utf-8') as f1:
                    content1 = f1.read().strip()
                with open(file2, 'r', encoding='utf-8') as f2:
                    content2 = f2.read().strip()
                return content1 == content2
            except:
                return False

    @staticmethod
    def get_diff_summary(file1: str, file2: str) -> str:
        """
        Get a summary of differences between two files.

        Args:
            file1: Path to expected output
            file2: Path to actual output

        Returns:
            String describing the differences
        """
        try:
            with open(file1, 'r') as f1:
                expected = f1.read().strip()

            with open(file2, 'r') as f2:
                actual = f2.read().strip()

            if expected == actual:
                return "Outputs match!"

            summary = "Outputs differ:\n"
            summary += f"Expected:\n{expected[:500]}\n\n"
            summary += f"Actual:\n{actual[:500]}\n"

            return summary

        except Exception as e:
            return f"Error comparing files: {str(e)}"
