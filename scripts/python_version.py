import platform

major: str
minor: str
patch: str
major, minor, patch = platform.python_version_tuple()
print(f"{major}{minor}")
