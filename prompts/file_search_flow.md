# SOTA File Search & Analysis Flow

Optimized flow for locating, grepping, and analyzing content within the `files` domain.

## Pattern 1: Recursive Search
When looking for specific file patterns (e.g., `.tsx` or `.py` files):
```json
{
  "domain": "files",
  "action": "search_files",
  "payload": { 
    "path": "[root]", 
    "search_pattern": "*.[ext]", 
    "recursive": true 
  }
}
```

## Pattern 2: Deep Grep
When looking for specific strings or symbols:
```json
{
  "domain": "files",
  "action": "grep_file",
  "payload": { 
    "path": "[file_or_dir]", 
    "search_pattern": "[regex]", 
    "recursive": true 
  }
}
```

## Pattern 3: Metadata Inspection
When checking file existence or metadata BEFORE modifying:
```json
{
  "domain": "files",
  "action": "get_file_info",
  "payload": { "path": "[file_path]" }
}
```

---
Consolidated via Universal Actuator Federation
