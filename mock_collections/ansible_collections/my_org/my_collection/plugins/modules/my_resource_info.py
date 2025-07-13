#!/usr/bin/python

DOCUMENTATION = '''
---
module: my_resource_info
short_description: Gathers information about my resource.
options:
    name:
        description:
            - Name of the resource to get info about.
        required: false
        type: str
'''

EXAMPLES = '''
- name: Get resource info
  my_org.my_collection.my_resource_info:
'''

def main():
    pass

if __name__ == '__main__':
    main()
