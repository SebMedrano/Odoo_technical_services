from odoo.tests.common import TransactionCase


class TestSaleOrderRepairFields(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Customer'})
        cls.user1 = cls.env['res.users'].create({
            'name': 'Tech User 1',
            'login': 'tech_user_1_test',
            'email': 'tech1@test.com',
        })
        cls.user2 = cls.env['res.users'].create({
            'name': 'Tech User 2',
            'login': 'tech_user_2_test',
            'email': 'tech2@test.com',
        })

    def _make_order(self):
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'service_type': 'repair',
        })

    def _make_repair(self, order, user=None, state='draft'):
        vals = {
            'name': 'TEST-REPAIR',
            'sale_order_id': order.id,
        }
        if user:
            vals['user_id'] = user.id
        repair = self.env['repair.order'].create(vals)
        if state != 'draft':
            repair.state = state
        return repair

    def test_no_repair_linked(self):
        """Sale order with no repair order has empty computed fields."""
        order = self._make_order()
        self.assertFalse(order.x_repair_state)
        self.assertFalse(order.x_repair_user_id)
        self.assertFalse(order.x_repair_id)

    def test_repair_state_computed(self):
        """x_repair_state reflects the linked repair order state."""
        order = self._make_order()
        repair = self._make_repair(order, state='draft')
        self.assertEqual(order.x_repair_state, 'draft')

    def test_repair_user_computed(self):
        """x_repair_user_id reflects the linked repair order user."""
        order = self._make_order()
        self._make_repair(order, user=self.user1)
        self.assertEqual(order.x_repair_user_id, self.user1)

    def test_repair_state_updates_when_repair_changes(self):
        """x_repair_state updates when the repair order state changes."""
        order = self._make_order()
        repair = self._make_repair(order, state='draft')
        self.assertEqual(order.x_repair_state, 'draft')
        repair.state = 'confirmed'
        self.assertEqual(order.x_repair_state, 'confirmed')
        repair.action_repair_start()
        self.assertEqual(order.x_repair_state, 'under_repair')

    def test_repair_user_updates_when_repair_changes(self):
        """x_repair_user_id updates when the repair order user changes."""
        order = self._make_order()
        repair = self._make_repair(order, user=self.user1)
        self.assertEqual(order.x_repair_user_id, self.user1)
        repair.user_id = self.user2
        self.assertEqual(order.x_repair_user_id, self.user2)

    def test_set_repair_user_inverse(self):
        """Writing x_repair_user_id on the sale order updates the repair order."""
        order = self._make_order()
        repair = self._make_repair(order, user=self.user1)
        self.assertEqual(repair.user_id, self.user1)
        order.x_repair_user_id = self.user2
        self.assertEqual(repair.user_id, self.user2)

    def test_first_repair_used_when_multiple(self):
        """When multiple repairs exist, only the first (oldest) is reflected."""
        order = self._make_order()
        repair1 = self._make_repair(order, user=self.user1)
        repair2 = self.env['repair.order'].create({
            'name': 'TEST-REPAIR-2',
            'sale_order_id': order.id,
            'user_id': self.user2.id,
        })
        # The One2many returns records ordered by id; [:1] picks the first
        self.assertEqual(order.x_repair_id, repair1)
        self.assertEqual(order.x_repair_user_id, self.user1)
        self.assertNotEqual(order.x_repair_id, repair2)

    def test_repair_id_cleared_when_unlinked(self):
        """Removing the sale_order_id from a repair clears the computed fields."""
        order = self._make_order()
        repair = self._make_repair(order, user=self.user1)
        self.assertEqual(order.x_repair_id, repair)
        repair.sale_order_id = False
        self.assertFalse(order.x_repair_id)
        self.assertFalse(order.x_repair_state)
        self.assertFalse(order.x_repair_user_id)


class TestRepairOrderBlocked(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Block Test Customer'})

    def _make_repair(self, state='confirmed'):
        repair = self.env['repair.order'].create({'name': 'BLOCK-TEST'})
        if state != 'draft':
            repair.state = state
        return repair

    def test_action_block_sets_state(self):
        """action_block transitions the repair to 'blocked'."""
        repair = self._make_repair(state='confirmed')
        repair.action_block()
        self.assertEqual(repair.state, 'blocked')

    def test_action_block_saves_previous_state_confirmed(self):
        """action_block saves 'confirmed' as the pre-block state."""
        repair = self._make_repair(state='confirmed')
        repair.action_block()
        self.assertEqual(repair.x_pre_block_state, 'confirmed')

    def test_action_block_saves_previous_state_under_repair(self):
        """action_block saves 'under_repair' as the pre-block state."""
        repair = self._make_repair(state='under_repair')
        repair.action_block()
        self.assertEqual(repair.x_pre_block_state, 'under_repair')

    def test_action_unblock_restores_confirmed(self):
        """action_unblock restores state to 'confirmed' when blocked from confirmed."""
        repair = self._make_repair(state='confirmed')
        repair.action_block()
        repair.action_unblock()
        self.assertEqual(repair.state, 'confirmed')

    def test_action_unblock_restores_under_repair(self):
        """action_unblock restores state to 'under_repair' when blocked from under_repair."""
        repair = self._make_repair(state='under_repair')
        repair.action_block()
        repair.action_unblock()
        self.assertEqual(repair.state, 'under_repair')

    def test_action_unblock_clears_pre_block_state(self):
        """action_unblock clears x_pre_block_state after restoring."""
        repair = self._make_repair(state='confirmed')
        repair.action_block()
        repair.action_unblock()
        self.assertFalse(repair.x_pre_block_state)

    def test_action_unblock_defaults_to_under_repair(self):
        """action_unblock falls back to 'under_repair' if x_pre_block_state is missing."""
        repair = self._make_repair(state='confirmed')
        repair.action_block()
        repair.x_pre_block_state = False
        repair.action_unblock()
        self.assertEqual(repair.state, 'under_repair')

    def test_sale_order_x_repair_state_shows_blocked(self):
        """x_repair_state on the linked sale order reflects 'blocked'."""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'service_type': 'repair',
        })
        repair = self.env['repair.order'].create({
            'name': 'BLOCK-SO-TEST',
            'sale_order_id': order.id,
        })
        repair.state = 'confirmed'
        repair.action_block()
        self.assertEqual(order.x_repair_state, 'blocked')

    def test_block_unblock_cycle_sale_order_state(self):
        """x_repair_state on sale order updates through a full block/unblock cycle."""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'service_type': 'repair',
        })
        repair = self.env['repair.order'].create({
            'name': 'BLOCK-CYCLE-TEST',
            'sale_order_id': order.id,
        })
        repair.state = 'under_repair'
        self.assertEqual(order.x_repair_state, 'under_repair')
        repair.action_block()
        self.assertEqual(order.x_repair_state, 'blocked')
        repair.action_unblock()
        self.assertEqual(order.x_repair_state, 'under_repair')
