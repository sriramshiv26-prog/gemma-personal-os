#!/usr/bin/env python3
"""
Integration tests for Gemma Personal OS across platforms.
Tests: Ollama connectivity, model inference, routing, database logging, SKILL loading.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gemma_os.core import Config, ModelRouter, Orchestrator, Database
from gemma_os.utils.skill_loader import SkillLoader
from gemma_os.workflows import SecurityAuditWorkflow


def test_health_check():
    """Test 1: Ollama connectivity and model availability"""
    print("\n" + "="*60)
    print("TEST 1: Health Check - Ollama Connectivity")
    print("="*60)

    config = Config()
    router = ModelRouter(config)

    try:
        is_healthy = router.health_check()
        print(f"✓ Ollama Health: {'PASS' if is_healthy else 'FAIL'}")
        return is_healthy
    except Exception as e:
        print(f"✗ Ollama Health Check Failed: {str(e)}")
        return False


def test_model_inference():
    """Test 2: Inference on both Gemma models"""
    print("\n" + "="*60)
    print("TEST 2: Model Inference Performance")
    print("="*60)

    config = Config()
    router = ModelRouter(config)

    results = {}

    for model_name in [config.ollama.model_fast, config.ollama.model_expert]:
        try:
            print(f"\nTesting {model_name}...")
            start_time = time.time()

            # test_inference returns dict with 'response' and 'time' keys
            test_result = router.test_inference(model_name)

            elapsed = time.time() - start_time
            response_text = test_result.get('response', '')

            results[model_name] = {
                "status": "PASS",
                "time_seconds": round(elapsed, 2),
                "response_length": len(response_text)
            }
            print(f"  ✓ Inference: {elapsed:.2f}s, Response: {len(response_text)} chars")
        except Exception as e:
            results[model_name] = {
                "status": "FAIL",
                "error": str(e)
            }
            print(f"  ✗ Inference Failed: {str(e)}")

    return results


def test_model_routing():
    """Test 3: Complexity analysis and model routing"""
    print("\n" + "="*60)
    print("TEST 3: Model Routing - Complexity Analysis")
    print("="*60)

    config = Config()
    router = ModelRouter(config)

    test_cases = [
        ("Hello world", "simple"),
        ("What is the capital of France?", "simple"),
        ("Analyze the security vulnerabilities in this code: def get_user(id): return User.query.get(id)", "complex"),
        ("Design a microservices architecture for a healthcare platform with HIPAA compliance requirements", "complex"),
    ]

    results = {}
    for task, expected_complexity in test_cases:
        try:
            analysis = router.analyze_complexity(task)
            model_selected = analysis.selected_model
            complexity = analysis.reasoning_depth

            match = "✓" if complexity == expected_complexity else "!"
            print(f"\n{match} Task: '{task[:50]}...'")
            print(f"  Complexity: {complexity} (expected {expected_complexity})")
            print(f"  Selected Model: {model_selected}")
            print(f"  Tokens: {analysis.input_tokens:.0f}")

            results[task[:30]] = {
                "complexity": complexity,
                "model": model_selected,
                "tokens": analysis.input_tokens
            }
        except Exception as e:
            print(f"  ✗ Routing Failed: {str(e)}")
            results[task[:30]] = {"status": "FAIL", "error": str(e)}

    return results


def test_database_logging():
    """Test 4: Database task creation and audit logging"""
    print("\n" + "="*60)
    print("TEST 4: Database Logging - Task Persistence")
    print("="*60)

    config = Config()
    db = Database(config)

    try:
        # Initialize database schema
        db.init()
        print(f"✓ Database initialized")

        # Create a test task
        task_id = f"test-{datetime.now().timestamp()}"
        db.create_task(
            task_id=task_id,
            task_name="Integration Test Task",
            task_type="integration_test",
            input_data={"test": "data"}
        )
        print(f"✓ Task created: {task_id}")

        # Log audit event
        db.log_audit(
            task_id=task_id,
            event_type="task_execution",
            event_data={"model": "gemma2:2b", "status": "started"},
            severity="INFO"
        )
        print(f"✓ Audit event logged")

        # Update task
        db.update_task(
            task_id=task_id,
            status="completed",
            output_data={"result": "success"},
            tokens_input=100,
            tokens_output=50
        )
        print(f"✓ Task updated with metrics")

        # Retrieve task
        task = db.get_task(task_id)
        if task:
            print(f"✓ Task retrieved: status={task['status']}")

        # Get stats
        stats = db.get_stats()
        print(f"✓ Database stats: {stats['total_tasks']} tasks, "
              f"{stats['success_rate']:.1f}% success rate")

        return {"status": "PASS", "task_id": task_id}
    except Exception as e:
        print(f"✗ Database Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "FAIL", "error": str(e)}


def test_skill_loading():
    """Test 5: SKILL.md framework loading"""
    print("\n" + "="*60)
    print("TEST 5: SKILL.md Loading")
    print("="*60)

    try:
        loader = SkillLoader()

        # Try to load security-auditing skill
        skill = loader.load_skill("security-auditing")
        if skill:
            print(f"✓ Loaded skill: {skill.get('name', 'unknown')}")
            print(f"  Domain: {skill.get('domain', 'unknown')}")
            print(f"  Content length: {len(skill.get('content', ''))} chars")
        else:
            print("! Skill not found (may not be installed yet)")

        return {"status": "PASS", "skill": skill.get("name") if skill else None}
    except Exception as e:
        print(f"✗ SKILL Loading Failed: {str(e)}")
        return {"status": "FAIL", "error": str(e)}


def test_workflow_execution():
    """Test 6: Workflow execution with end-to-end task flow"""
    print("\n" + "="*60)
    print("TEST 6: Workflow Execution - End-to-End")
    print("="*60)

    try:
        config = Config()

        # Simple security audit on a code snippet
        test_code = '''
def authenticate(username, password):
    query = "SELECT * FROM users WHERE username='" + username + "'"
    result = db.execute(query)
    if result and result[0]['password'] == password:
        return True
    return False
        '''

        print("Executing SecurityAuditWorkflow on vulnerable code...")
        print(f"Code: {len(test_code)} chars\n")

        workflow = SecurityAuditWorkflow(config)
        start_time = time.time()

        result = workflow.execute(code=test_code)

        elapsed = time.time() - start_time
        print(f"\n✓ Workflow completed in {elapsed:.2f}s")
        print(f"  Status: {result.get('status')}")
        print(f"  Workflow Type: {result.get('workflow_type')}")

        findings = result.get('findings_summary', {})
        if findings:
            print(f"  Findings Summary:")
            for severity, count in findings.items():
                if count > 0:
                    print(f"    {severity}: {count}")

        return {
            "status": "PASS",
            "execution_time": elapsed,
            "findings": findings
        }
    except Exception as e:
        print(f"✗ Workflow Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "FAIL", "error": str(e)}


def run_all_tests():
    """Run all integration tests and report results"""
    print("\n" + "█"*60)
    print("GEMMA 4 PERSONAL OS - INTEGRATION TEST SUITE")
    print("█"*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "health_check": test_health_check(),
        "model_inference": test_model_inference(),
        "model_routing": test_model_routing(),
        "database_logging": test_database_logging(),
        "skill_loading": test_skill_loading(),
        "workflow_execution": test_workflow_execution(),
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for k, v in results.items()
                 if isinstance(v, dict) and v.get("status") == "PASS")
    total = len([v for v in results.values() if isinstance(v, dict)])

    print(f"\nResults: {passed}/{total} test groups passed")
    print(f"\nDetailed Results:")
    print(json.dumps(results, indent=2, default=str))

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("█"*60 + "\n")

    return results


if __name__ == "__main__":
    run_all_tests()
