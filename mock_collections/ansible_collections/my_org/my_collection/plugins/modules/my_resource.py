#!/usr/bin/python

DOCUMENTATION = '''
---
module: my_resource
short_description: Manages my resource.
options:
    name:
        description:
            - Name of the resource.
        required: true
        type: str
    state:
        description:
            - The state of the resource.
        required: false
        type: str
        choices:
            - present
            - absent
        default: present
'''

EXAMPLES = '''
- name: Create resource
  my_org.my_collection.my_resource:
    name: my_resource_name
    state: present
'''

def main():
    pass

if __name__ == '__main__':
    main()
