# TOOL CONTRACT v2

## Registry
read_file
search_knowledge
analyze_image
run_python
create_docx
create_xlsx
calculator

## Common interface
Tool:
- name
- description
- input_schema
- execute()
- timeout
- permissions

## read_file
Input: {"file_id":"string"}
Only controlled workspace files.
Reject traversal and absolute host paths.

## search_knowledge
Input: {"query":"string","top_k":1..10}
Returns Source objects.

## analyze_image
Input: {"file_id":"string","instruction":"string"}
Uses local vision model only.

## run_python
Input:
{"code":"string","input_files":["FILE-..."]}
Execution must be isolated, network-disabled and resource-limited.

## create_docx
Input:
{"title":"string","sections":[{"heading":"string","content":"string"}]}
Returns Artifact.

## create_xlsx
Input:
{"filename":"string","sheets":[{"name":"string","rows":[[]]}]}
Returns Artifact.

## calculator
Input:
{"expression":"string"}
No network or arbitrary code.

## Tool result
All tools return:
{
  "success": true,
  "result": {},
  "error": null
}

## Denial
Security-sensitive invalid requests return status=denied and an audit event.
