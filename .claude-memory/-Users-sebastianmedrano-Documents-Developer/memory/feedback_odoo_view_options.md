---
name: Odoo _get_view options format
description: When modifying field options in Odoo 18 _get_view overrides, must use Python dict notation not JSON
type: feedback
originSessionId: 36785d4c-7291-4fc6-a025-f92af3be6ee8
---
Use `ast.literal_eval` to parse and `str()` to serialize field options in `_get_view` overrides — NOT `json.loads`/`json.dumps`.

**Why:** Odoo 18's JavaScript expression evaluator (used client-side to parse field `options` attributes) expects Python dict notation with `True`/`False`. `json.dumps` produces lowercase `true`/`false` which the JS evaluator treats as undefined, silently ignoring the option. This caused `no_quick_create: true` (JSON) to have no effect even though the arch was correctly modified.

**How to apply:** Any time modifying an `options` attribute in `_get_view`:
```python
import ast
try:
    opts = ast.literal_eval(node.get('options', '{}'))
except (ValueError, SyntaxError):
    opts = {}
opts['no_quick_create'] = True
node.set('options', str(opts))  # produces {'no_quick_create': True} — Python style
```
Same applies to static XML: use `{'no_quick_create': True}` not `{"no_quick_create": true}`.
