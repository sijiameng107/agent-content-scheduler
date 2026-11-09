# live execution results

Executed 9/9; passed 7. Model: glm-4-flash-250414.

| Case | Pass | Evidence |
|---|---|---|
| normal | False | [Trace](normal/output.json), [assertions](normal/assertions.json) |
| missing | True | [Trace](missing/output.json), [assertions](missing/assertions.json) |
| risk | True | [Trace](risk/output.json), [assertions](risk/assertions.json) |
| conflict | True | [Trace](conflict/output.json), [assertions](conflict/assertions.json) |
| save_failure | True | [Trace](save_failure/output.json), [assertions](save_failure/assertions.json) |
| duplicate_first | True | [Trace](duplicate_first/output.json), [assertions](duplicate_first/assertions.json) |
| duplicate_repeat | True | [Trace](duplicate_repeat/output.json), [assertions](duplicate_repeat/assertions.json) |
| changed_occupancy | True | [Trace](changed_occupancy/output.json), [assertions](changed_occupancy/assertions.json) |
| confirmed_alternative | False | [Trace](confirmed_alternative/output.json), [assertions](confirmed_alternative/assertions.json) |

Review at least two traces for observation-dependent actions; automated assertions alone are insufficient.
