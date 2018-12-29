from mpf.core.custom_code import CustomCode

class Magnaramp(CustomCode):

    def on_load(self):
        self.info_log('Enabling')

        self.machine.events.add_handler('ball_started', self.enable)
        self.machine.events.add_handler('ball_ended', self.disable)

    def enable(self, **kwargs):
        del kwargs

        self.info_log('Enabling')

        self.machine.switch_controller.add_switch_handler(
            's_top_basket_enter', self.enable_magnet)

    def disable(self, **kwargs):
        del kwargs

        self.info_log('Disabling')

        self.machine.switch_controller.remove_switch_handler(
            's_top_basket_enter', self.enable_magnet)

        self.disable_magnet()

    def enable_magnet(self, **kwargs):
        del kwargs

        self.info_log('Enabling Magnet')

        self.machine.coils['c_basket_magnet'].enable()
        self.delay.add(500, self.disable_magnet)

    def disable_magnet(self, **kwargs):
        del kwargs

        self.machine.coils['c_basket_magnet'].disable()
        self.info_log('Disabling Magnet')
