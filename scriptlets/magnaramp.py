from mpf.core.custom_code import CustomCode

class Magnaramp(CustomCode):

    def on_load(self):
        self.magnaramp_in_progress = False

        if self.machine.switch_controller.is_active('s_jump_ball_vuk'):
            self.upkick_to_magnet()

    def enable(self):
        self.machine.switch_controller.add_switch_handler(
            's_jump_ball_vuk', self.upkick_to_magnet())

    def upkick_to_magnet(self):
        self.info_log('You hit the switch!!')
        self.enable_magnet()
        # have a check to make sure there isn't already a ball on the magnet during multiball

    def disable_magnet(self):
        self.info_log('magnet disabled')

    def choose_lane(self):
        disable_magnet()

        if self.machine.get_machine_var('magnaramp_left'):
            self.ramp_left()
        else:
            self.ramp_right()

    def enable_magnet(self):
        self.info_log('magnet enabled')
        self.info_log('setting timer')
        self.delay.add(2, self.choose_lane)

    def ramp_left(self):
        self.info_log('ramp_left')

    def ramp_right(self):
        self.info_log('ramp_right')
