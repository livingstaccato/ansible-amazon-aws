#!/usr/bin/env python

import os
import sys
import argparse
import json
from pathlib import Path
import yaml

def parse_module_doc(module_path):
    """
    Parse the DOCUMENTATION string from an Ansible module file.
    """
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None  # Can't read file

    doc_start = content.find('DOCUMENTATION = """')
    if doc_start == -1:
        doc_start = content.find("DOCUMENTATION = '''")
    if doc_start == -1:
        return None

    # Adjust for the length of the opening marker
    doc_start += len('DOCUMENTATION = """') if '"""' in content else len("DOCUMENTATION = '''")

    doc_end = content.find('"""', doc_start)
    if doc_end == -1:
        doc_end = content.find("'''", doc_start)
    if doc_end == -1:
        return None

    doc_string = content[doc_start:doc_end]

    try:
        doc = yaml.safe_load(doc_string)
        return doc
    except yaml.YAMLError:
        return None

def analyze_module(module_name, doc):
    """
    Analyze the module's documentation to determine CRUD operations and arguments.
    """
    if not doc or 'module' not in doc:
        return None

    crud = {"C": False, "R": False, "U": False, "D": False}

    # Heuristic for Read operations
    if module_name.endswith(('_info', '_facts')):
        crud['R'] = True

    options = doc.get('options', {})

    # Heuristic for CUD operations based on 'state' parameter
    if 'state' in options and options['state'] and isinstance(options['state'], dict):
        choices = options['state'].get('choices', [])
        if 'present' in choices:
            crud['C'] = True
            crud['U'] = True
        if 'absent' in choices:
            crud['D'] = True

    # If it's not a Read module and has no state parameter, assume it's a one-shot
    # action module. We can categorize this as "Create/Update" since it causes a change.
    if not crud['R'] and not any([crud['C'], crud['U'], crud['D']]):
         crud['C'] = True
         crud['U'] = True

    return {
        "crud_operations": crud,
        "arguments": options
    }

def main():
    parser = argparse.ArgumentParser(
        description="""
        Parses Ansible collection modules to determine their CRUD (Create, Read, Update, Delete)
        capabilities and arguments based on documentation and conventions.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("collection_name", help="The name of the collection to parse (e.g., community.general)")
    parser.add_argument(
        "--collections-path",
        required=True,
        help="Base path to your ansible_collections directory (e.g., ~/.ansible/collections/ansible_collections)."
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of modules to parse (default: 0 for no limit).")
    parser.add_argument("-o", "--output-file", help="File to write JSON output to. If not provided, prints to stdout.")
    args = parser.parse_args()

    collections_base_path = Path(args.collections_path)

    if not collections_base_path.is_dir():
        print(f"Error: Collections path '{collections_base_path}' not found or not a directory.", file=sys.stderr)
        sys.exit(1)

    collection_path_str = args.collection_name.replace('.', '/')
    collection_path = collections_base_path / collection_path_str

    if not collection_path.is_dir():
        print(f"Error: Collection '{args.collection_name}' not found at '{collection_path}'", file=sys.stderr)
        sys.exit(1)

    modules_path = collection_path / "plugins" / "modules"
    if not modules_path.is_dir():
        print(f"Info: No 'modules' directory found for collection '{args.collection_name}'.", file=sys.stderr)
        sys.exit(0)

    results = {}

    all_modules = [entry.path for entry in os.scandir(modules_path) if entry.name.endswith('.py')]
    all_modules.sort()

    limit = args.limit if args.limit > 0 else len(all_modules)

    for i, module_file_path in enumerate(all_modules):
        if i >= limit:
            break

        module_file = Path(module_file_path)
        if module_file.name == '__init__.py':
            continue

        doc = parse_module_doc(module_file)
        if doc:
            analysis = analyze_module(module_file.stem, doc)
            if analysis:
                results[module_file.stem] = analysis

    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"Successfully parsed {len(results)} modules. Output written to {args.output_file}", file=sys.stderr)
    else:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
