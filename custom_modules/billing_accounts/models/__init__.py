# Odoo loads these files in order.
# service_worktag must come first because sale_order and
# account_move reference it — Python needs to know it exists first.
from . import service_worktag
from . import sale_order
from . import account_move
