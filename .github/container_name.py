#!/usr/bin/env python3
import sys

container_name = sys.argv[1]
prefix = sys.argv[2]

# print(f"Initial container name is {container_name}")
# print(f"Desired prefix is {prefix}")

container, tag = container_name.split(':', 1)
# print(f"Container is {container}")
# print(f"Tag is {tag}")

registry, name = container.rsplit('/', 1)

container = f"{registry}/{prefix}-{name}:{tag}"
print(container)
