# Load order matters — service_worktag first as other models reference it
from . import service_worktag
from . import res_partner
from . import product_template
from . import sale_order
from . import sale_order_line
from . import account_move
