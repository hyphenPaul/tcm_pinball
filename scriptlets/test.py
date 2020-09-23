from mpf.core.custom_code import CustomCode

class Test(CustomCode):

    def on_load(self):
        self.info_log('Test Enabling')

        self.machine.events.add_handler('cmd_test_flipper_left', self.test_flipper)

    def test_flipper(self, **kwargs):
        self.info_log("\n\n***\n\n")
        self.info_log(self.machine.accruals.escape_multiball_shot_accrual)
        self.info_log("\n\n***\n\n")
        self.info_log(self.machine.accruals.escape_multiball_shot_accrual.value)
        self.info_log("\n\n***\n\n")

