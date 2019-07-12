from mpf.core.custom_code import CustomCode

class Magnavuk(CustomCode):

    def on_load(self):
        self.info_log('Enabling')

        self.enabled = False
        self.auto_fire = self.machine.get_machine_var('magnavuk_auto_fire')

        if self.machine.switch_controller.is_active('s_jump_ball_vuk'):
            self.delay.add(1000, self.clear_ball)

        self.machine.events.add_handler('ball_started', self.enable)
        self.machine.events.add_handler('ball_ended', self.disable)
        self.machine.events.add_handler('cmd_custom_magna_vuk_handler', self.add_custom_vuk_handler)

    def enable(self, **kwargs):
        del kwargs

        if self.enabled:
           return

        self.info_log('Enabling')

        self.delay.remove('ball_clear')

        if self.auto_fire:
            self.add_auto_vuk_handler()

        self.machine.events.add_handler(
            'magnavuk_vuk_firing', self.enable_magnet)
        self.machine.events.add_handler(
            'magnavuk_magnet_disabled', self.choose_lane)

        self.enabled = True

    def disable(self, **kwargs):
        del kwargs

        self.info_log('Disabling')

        self.remove_auto_vuk_handler()
        self.machine.events.remove_handler_by_event(
            'magnavuk_vuk_firing', self.enable_magnet)
        self.machine.events.remove_handler_by_event(
            'magnavuk_magnet_disabled', self.choose_lane)

        self.disable_magnet()

        self.enabled = False

    def clear_ball(self):
        self.info_log('Clearing ball')

        self.enable()
        self.fire_vuk()

        self.delay.add(2000, self.check_if_clear, 'ball_clear')

    def check_if_clear(self, **kwargs):
        del kwargs

        self.info_log('Check if clear')

        if self.machine.switch_controller.is_active('s_jump_ball_vuk'):
            self.clear_ball()
        else:
            self.disable()

    def remove_auto_vuk_handler(self):
        self.info_log('Remove handler')
        self.machine.switch_controller.remove_switch_handler(
            's_jump_ball_vuk', self.fire_vuk, 1, 500)

    def add_auto_vuk_handler(self, **kwargs):
        self.info_log('Add handler')
        self.machine.switch_controller.add_switch_handler(
            's_jump_ball_vuk', self.fire_vuk, 1, 500)

    def add_custom_vuk_handler(self, **kwargs):
        self.info_log('add_custom_vuk_handler')
        self.info_log(kwargs)

        self.remove_auto_vuk_handler()
        self.machine.switch_controller.add_switch_handler(
            's_jump_ball_vuk', self.handle_custom_vuk_event, 1, 500, False, kwargs)

    def handle_custom_vuk_event(self, **kwargs):
        self.machine.events.post(kwargs['switch_hit_evnt'])
        self.machine.events.add_handler(
            kwargs['fire_vuk_evnt'], self.fire_vuk, 1, kwargs)

    def fire_vuk(self, **kwargs):
        self.info_log('**************************************************')
        self.info_log('**************************************************')
        self.info_log(kwargs.get('coil_direction')) # not working
        self.info_log('**************************************************')
        self.info_log('**************************************************')

        self.info_log('Vuk firing')

        self.machine.events.post('cmd_magnavuk_firing')
        self.machine.events.post('magnavuk_vuk_firing')
        self.machine.coils['c_jump_ball_vuk'].pulse()

    def disable_magnet(self, **kwargs):
        del kwargs

        self.info_log('magnet disabled')
        self.machine.coils['c_jump_ball_magnet'].disable()
        self.machine.events.post('magnavuk_magnet_disabled')

    def choose_lane(self, **kwargs):
        del kwargs

        if self.machine.get_machine_var('magnavuk_left'):
            self.ramp_left()
        else:
            self.ramp_right()

        self.toggle_direction()

    def enable_magnet(self, **kwargs):
        del kwargs

        self.info_log('magnet enabled')
        self.machine.coils['c_jump_ball_magnet'].enable()
        self.delay.add(500, self.disable_magnet)

    def toggle_direction(self):
        self.machine.set_machine_var(
            'magnavuk_left', not self.machine.get_machine_var('magnavuk_left'))

    def ramp_left(self):
        self.info_log('ramp_left')
        self.machine.events.post('magnavuk_shot_left')
        self.machine.coils['c_jump_ball_right_kicker'].pulse()

    def ramp_right(self):
        self.info_log('ramp_right')
        self.machine.events.post('magnavuk_shot_right')
        self.machine.coils['c_jump_ball_top_kicker'].pulse()
