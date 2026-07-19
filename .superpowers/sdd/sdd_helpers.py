import os
import sys
import re
import shutil
import difflib

def get_repo_root():
    # Since there's no Git, we resolve root as the directory containing .superpowers folder
    current = os.path.abspath(os.getcwd())
    while current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, '.superpowers')):
            return current
        current = os.path.dirname(current)
    return os.path.abspath(os.getcwd())

def get_sdd_dir():
    root = get_repo_root()
    sdd_dir = os.path.join(root, '.superpowers', 'sdd')
    os.makedirs(sdd_dir, exist_ok=True)
    return sdd_dir

def get_backup_dir(task_number):
    sdd_dir = get_sdd_dir()
    backup_dir = os.path.join(sdd_dir, 'backups', f"task-{task_number}")
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def backup_files(task_number, files_list):
    backup_dir = get_backup_dir(task_number)
    root = get_repo_root()
    
    for fpath in files_list:
        # Resolve to absolute path
        abs_path = os.path.abspath(fpath) if os.path.isabs(fpath) else os.path.abspath(os.path.join(root, fpath))
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            rel_path = os.path.relpath(abs_path, root)
            dest_path = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(abs_path, dest_path)
            print(f"Backed up {rel_path} -> {dest_path}")
        else:
            # If it's a new file, we back it up as an empty file so diff works correctly
            rel_path = os.path.relpath(abs_path, root)
            dest_path = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write('')
            print(f"Initialized new file backup for {rel_path}")

def generate_diff(task_number, files_list, out_file=None):
    root = get_repo_root()
    sdd_dir = get_sdd_dir()
    backup_dir = get_backup_dir(task_number)
    
    if not out_file:
        out_file = os.path.join(sdd_dir, f"review-task-{task_number}.diff")
        
    diff_output = []
    diff_output.append(f"# Review package for Task {task_number} (Python Diff)")
    diff_output.append(f"# Base Backup: {backup_dir}\n")
    
    files_changed_list = []
    
    for fpath in files_list:
        abs_path = os.path.abspath(fpath) if os.path.isabs(fpath) else os.path.abspath(os.path.join(root, fpath))
        rel_path = os.path.relpath(abs_path, root)
        
        backup_path = os.path.join(backup_dir, rel_path)
        
        # Read backup lines
        backup_lines = []
        if os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8', errors='replace') as f:
                backup_lines = f.readlines()
                
        # Read current lines
        current_lines = []
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                current_lines = f.readlines()
                
        # Generate unified diff
        diff = list(difflib.unified_diff(
            backup_lines, current_lines,
            fromfile=os.path.join('a', rel_path),
            tofile=os.path.join('b', rel_path),
            n=10 # Use 10 lines of context (like git diff -U10)
        ))
        
        if diff:
            files_changed_list.append(rel_path)
            diff_output.append(f"diff --git a/{rel_path} b/{rel_path}")
            diff_output.extend([line.rstrip('\n') for line in diff])
            diff_output.append("")
            
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(diff_output) + '\n')
        
    print(f"wrote {out_file}: {len(files_changed_list)} file(s) changed, {os.path.getsize(out_file)} bytes")
    return out_file

def task_brief(plan_file, task_number, out_file=None):
    if not os.path.exists(plan_file):
        print(f"Error: plan file not found {plan_file}", file=sys.stderr)
        sys.exit(2)
        
    sdd_dir = get_sdd_dir()
    if not out_file:
        out_file = os.path.join(sdd_dir, f"task-{task_number}-brief.md")
        
    with open(plan_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.splitlines()
    task_lines = []
    intask = False
    infence = False
    
    header_pattern = re.compile(rf"^#+[ \t]+Task[ \t]+{task_number}(?:[^0-9]|$)", re.IGNORECASE)
    next_task_pattern = re.compile(r"^#+[ \t]+Task[ \t]+[0-9]+(?:[^0-9]|$)", re.IGNORECASE)
    
    for line in lines:
        if line.startswith('```'):
            infence = not infence
            
        if not infence:
            if header_pattern.match(line):
                intask = True
            elif next_task_pattern.match(line) and intask:
                intask = False
                
        if intask:
            task_lines.append(line)
            
    if not task_lines:
        print(f"Error: task {task_number} not found in {plan_file}", file=sys.stderr)
        sys.exit(3)
        
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(task_lines) + '\n')
        
    print(f"wrote {out_file}: {len(task_lines)} lines")
    return out_file

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage:", file=sys.stderr)
        print("  python sdd_helpers.py brief <PLAN_FILE> <TASK_NUMBER>", file=sys.stderr)
        print("  python sdd_helpers.py backup <TASK_NUMBER> <FILE1> [FILE2 ...]", file=sys.stderr)
        print("  python sdd_helpers.py diff <TASK_NUMBER> <FILE1> [FILE2 ...]", file=sys.stderr)
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == 'brief':
        plan = sys.argv[2]
        task = sys.argv[3]
        task_brief(plan, task)
    elif cmd == 'backup':
        task = sys.argv[2]
        files = sys.argv[3:]
        backup_files(task, files)
    elif cmd == 'diff':
        task = sys.argv[2]
        files = sys.argv[3:]
        generate_diff(task, files)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
