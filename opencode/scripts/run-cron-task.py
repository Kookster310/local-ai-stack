#!/usr/bin/env python3
"""
Modular context wrapper for cron tasks
Ensures proper context loading and logs to cron.log for any prompt/task
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime

def log_to_cron(task_name, message):
    """Log to cron.log as required by AGENTS.md"""
    with open('/workspace/logs/cron.log', 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {task_name} | {message}\n")

def run_with_context(task_name, prompt, log_file=None):
    """
    Run an opencode task with proper context loading
    """
    log_to_cron(task_name, "started")
    
    try:
        # Ensure logs directory exists
        os.makedirs('/workspace/logs', exist_ok=True)
        
        # Set environment variables to ensure context loading
        env = os.environ.copy()
        env['PYTHONPATH'] = '/workspace'
        env['WORKSPACE'] = '/workspace'
        
        # Build the opencode command
        cmd = [
            '/usr/local/bin/opencode',
            'run',
            '--model',
            'opencode/big-pickle',
            prompt
        ]
        
        # Create a log file for this run if specified
        if log_file:
            log_path = f'/workspace/logs/{log_file}'
            with open(log_path, 'a') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Cron Task Run: {task_name} - {datetime.now().isoformat()}\n")
                f.write(f"Prompt: {prompt}\n")
                f.write(f"{'='*50}\n")
                
                result = subprocess.run(
                    cmd,
                    env=env,
                    cwd='/workspace',
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    text=True
                )
        else:
            result = subprocess.run(
                cmd,
                env=env,
                cwd='/workspace',
                capture_output=True,
                text=True
            )
        
        if result.returncode == 0:
            log_to_cron(task_name, "completed")
        else:
            log_to_cron(task_name, f"failed: return code {result.returncode}")
            if not log_file and result.stderr:
                log_to_cron(task_name, f"stderr: {result.stderr[:200]}...")
            
        return result.returncode
        
    except Exception as e:
        log_to_cron(task_name, f"failed: {str(e)}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='Run opencode task with context and logging')
    parser.add_argument('task_name', help='Name of the task for logging')
    parser.add_argument('prompt', help='Prompt to pass to opencode')
    parser.add_argument('--log', help='Log file name (without path)')
    
    args = parser.parse_args()
    
    return run_with_context(args.task_name, args.prompt, args.log)

if __name__ == '__main__':
    sys.exit(main())