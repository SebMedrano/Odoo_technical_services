# Load order matters:
# service_worktag first — other models reference it
# res_partner second — adds One2many back to worktags
# sale_order and account_move last — reference service.worktag
from . import service_worktag
from . import res_partner
from . import sale_order
from . import account_move
