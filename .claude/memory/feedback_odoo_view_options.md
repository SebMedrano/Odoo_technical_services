---
name: Odoo _get_view options format
description: Odoo 18 view modification patterns — options format, hiding tabs, name search
type: feedback
originSessionId: db77456c-e97a-4cd2-a596-93edc0415bfe
---
## Field options in `_get_view`
Use `ast.literal_eval` to parse and `str()` to serialize field options — NOT `json.loads`/`json.dumps`.

**Why:** Odoo 18's JS evaluator expects Python dict notation with `True`/`False`. `json.dumps` produces lowercase `true`/`false` which is silently ignored.

```python
import ast
try:
    opts = ast.literal_eval(node.get('options', '{}'))
except (ValueError, SyntaxError):
    opts = {}
opts['no_quick_create'] = True
node.set('options', str(opts))  # {'no_quick_create': True} — Python style
```
Same applies to static XML: use `{'no_quick_create': True}` not `{"no_quick_create": true}`.

## Hiding notebook tabs (`<page>`) for specific roles
`groups="..."` on a `<page>` element via xpath inheritance does NOT reliably hide the tab in Odoo 18. Use the `_get_view` Python override instead:

```python
if not self.env.user.has_group('techservices_groups.group_manager'):
    for node in arch.xpath("//page[@name='page_miscellaneous']"):
        node.set('invisible', 'True')
```

**Why:** The xpath `groups` attribute approach silently fails for page elements — confirmed on the repair form's Miscellaneous tab.
**How to apply:** Any time a notebook tab needs role-based hiding, go straight to `_get_view` with `node.set('invisible', 'True')`.

## Many2one search in Odoo 18
`_name_search` is NOT called by `name_search` in Odoo 18. `name_search` directly searches on `display_name`. Use `_rec_names_search` to define which fields are searched:

```python
_rec_names_search = ['make', 'model', 'serial_number', 'partner_id.name']
```

**Why:** Odoo 18's `name_search` calls `search_fetch([('display_name', operator, name)])`, which triggers `_search_display_name`, which reads `_rec_names_search`. Overriding `_name_search` has no effect.
**How to apply:** Always use `_rec_names_search` (not `_name_search`) for custom Many2one search in Odoo 18.

## Avoid `_rec_name = 'display_name'`
Never set `_rec_name = 'display_name'` on a model. It causes infinite recursion: `_name_search` → domain `[('display_name', ilike, term)]` → `_search_display_name` → `_name_search` → loop. Thread times out at 120s.

**How to apply:** Use `_rec_names_search` for composite display search, and keep `_rec_name` pointing to a real stored field (or omit it to use the default `name`).
