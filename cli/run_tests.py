#!/usr/bin/env python3
"""
Automated test runner for context awareness system
Run with: python3 run_tests.py
"""

import os
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

sys.path.insert(0, os.path.dirname(__file__))

from context import (
    get_relevant_context,
    index_codebase,
    infer_target_files,
    search_codebase,
)

console = Console()


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.context_dir = os.getcwd()

    def test(self, name: str, query: str, expected_keywords: list, test_type: str = "search"):
        """Run a single test"""
        console.print(f"\n[cyan]Testing:[/cyan] {name}")
        console.print(f"[dim]Query: {query}[/dim]")

        start_time = time.time()

        try:
            if test_type == "search":
                results = search_codebase(query, self.context_dir, max_results=3)
                result_text = str(results)
            elif test_type == "context":
                context = get_relevant_context(query, self.context_dir, max_chunks=3)
                result_text = context
            elif test_type == "infer":
                files = infer_target_files(query, self.context_dir)
                result_text = str(files)
            else:
                result_text = ""

            elapsed = (time.time() - start_time) * 1000  # Convert to ms

            # Check if expected keywords are in results
            found = []
            missing = []
            for keyword in expected_keywords:
                if keyword.lower() in result_text.lower():
                    found.append(keyword)
                else:
                    missing.append(keyword)

            passed = len(missing) == 0

            if passed:
                console.print(f"[green]✓ PASSED[/green] ({elapsed:.0f}ms)")
                console.print(f"[dim]Found: {', '.join(found)}[/dim]")
                self.passed += 1
            else:
                console.print(f"[red]✗ FAILED[/red] ({elapsed:.0f}ms)")
                console.print(f"[yellow]Missing: {', '.join(missing)}[/yellow]")
                self.failed += 1

            self.results.append({
                "name": name,
                "query": query,
                "passed": passed,
                "time_ms": elapsed,
                "found": found,
                "missing": missing,
            })

        except Exception as e:
            console.print(f"[red]✗ ERROR: {e}[/red]")
            self.failed += 1
            self.results.append({
                "name": name,
                "query": query,
                "passed": False,
                "time_ms": 0,
                "error": str(e),
            })

    def run_all_tests(self):
        """Run complete test suite"""
        console.print(Panel(
            "[bold]Context Awareness Automated Test Suite[/bold]\n"
            "Running comprehensive tests on semantic search",
            style="bold blue"
        ))

        # First, ensure indexing works
        console.print("\n[yellow]Step 1: Indexing codebase...[/yellow]")
        start = time.time()
        try:
            collection = index_codebase(self.context_dir)
            count = collection.count()
            elapsed = time.time() - start
            console.print(f"[green]✓ Indexed {count} chunks in {elapsed:.1f}s[/green]")
        except Exception as e:
            console.print(f"[red]✗ Indexing failed: {e}[/red]")
            return

        console.print("\n[yellow]Step 2: Running test cases...[/yellow]")

        # Level 1: Basic Semantic Understanding
        console.print("\n[bold]Level 1: Basic Semantic Understanding[/bold]")

        self.test(
            "Function Discovery",
            "How does streaming work?",
            ["generate_response_streaming", "model.py"],
            test_type="search"
        )

        self.test(
            "UI/Theme Query",
            "What colors are used in the interface?",
            ["theme.py"],
            test_type="search"
        )

        self.test(
            "File Operations",
            "How are files written?",
            ["write_file", "file_ops.py"],
            test_type="search"
        )

        # Level 2: File Inference
        console.print("\n[bold]Level 2: File Inference[/bold]")

        self.test(
            "Explicit File Creation",
            "create test_utils.py with helpers",
            ["test_utils.py"],
            test_type="infer"
        )

        self.test(
            "Existing File Edit",
            "edit model.py to improve quality",
            ["model.py"],
            test_type="infer"
        )

        self.test(
            "Keyword-Based Inference",
            "add authentication features",
            ["auth"],  # Should suggest auth.py or authentication.py
            test_type="infer"
        )

        # Level 3: Cross-File Understanding
        console.print("\n[bold]Level 3: Cross-File Understanding[/bold]")

        self.test(
            "Related Functions",
            "Show me all file operation functions",
            ["write_file", "read_file", "file_ops"],
            test_type="search"
        )

        self.test(
            "Module Structure",
            "user interface and chat",
            ["chat", "theme"],
            test_type="search"
        )

        # Level 4: Complex Queries
        console.print("\n[bold]Level 4: Complex Queries[/bold]")

        self.test(
            "Multi-Concept Query",
            "How does the system process user input and generate responses?",
            ["chat", "model", "generate"],
            test_type="context"
        )

        self.test(
            "Natural Language Intent",
            "I want to improve the chat interface responsiveness",
            ["chat", "streaming"],
            test_type="search"
        )

        # Level 5: Edge Cases
        console.print("\n[bold]Level 5: Edge Cases[/bold]")

        self.test(
            "Non-Existent Concept",
            "Show me database connection pooling",
            [],  # Shouldn't crash, but won't find anything
            test_type="search"
        )

        self.test(
            "Very Generic Query",
            "code",
            [],  # Should return something without crashing
            test_type="search"
        )

    def show_summary(self):
        """Display test summary"""
        console.print("\n" + "="*80)
        console.print("\n[bold]Test Summary[/bold]\n")

        # Create results table
        table = Table(title="Test Results")
        table.add_column("Test Name", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Time (ms)", justify="right")

        for result in self.results:
            status = "[green]✓ PASS[/green]" if result["passed"] else "[red]✗ FAIL[/red]"
            time_str = f"{result.get('time_ms', 0):.0f}"
            table.add_row(result["name"], status, time_str)

        console.print(table)

        # Statistics
        total = self.passed + self.failed
        accuracy = (self.passed / total * 100) if total > 0 else 0
        avg_time = sum(r.get('time_ms', 0) for r in self.results) / len(self.results) if self.results else 0

        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total Tests: {total}")
        console.print(f"  Passed: [green]{self.passed}[/green]")
        console.print(f"  Failed: [red]{self.failed}[/red]")
        console.print(f"  Accuracy: [cyan]{accuracy:.1f}%[/cyan]")
        console.print(f"  Average Query Time: [cyan]{avg_time:.0f}ms[/cyan]")

        # Performance rating
        console.print(f"\n[bold]Performance Rating:[/bold]")
        if accuracy >= 90:
            console.print("[green]★★★★★ Excellent![/green]")
        elif accuracy >= 75:
            console.print("[yellow]★★★★☆ Good[/yellow]")
        elif accuracy >= 60:
            console.print("[yellow]★★★☆☆ Fair[/yellow]")
        else:
            console.print("[red]★★☆☆☆ Needs Improvement[/red]")

        console.print()


def main():
    """Main entry point"""
    runner = TestRunner()
    runner.run_all_tests()
    runner.show_summary()

    # Exit with proper code
    sys.exit(0 if runner.failed == 0 else 1)


if __name__ == "__main__":
    main()
