from mpf.core.custom_code import CustomCode

class Magnavuk(CustomCode):

    def on_load(self):
        self.info_log('Loading')

        self.enabled = False

        self.s_jump_ball_vuk_switch = self.machine.switches['s_jump_ball_vuk']

        if self.machine.switch_controller.is_active(self.s_jump_ball_vuk_switch):
            self.delay.add(1000, self.clear_ball)

        self.machine.events.add_handler('ball_started', self.enable)
        self.machine.events.add_handler('ball_ended', self.disable)

        # handler queue
        self.custom_switch_handler_queue = []
        self.machine.events.add_handler('cmd_custom_magna_vuk_queue_event', self.add_queue_event)
        self.machine.events.add_handler('cmd_clear_magna_vuk_queue', self.clear_queue)
        self.current_queue_event = None
        self.queue_callback_handler = None

    def clear_queue(self, **kwargs):
        del kwargs

        self.clear_callback_handler()
        self.custom_switch_handler_queue = []

    def add_queue_event(self, **kwargs):
        self.info_log('add_queue_event_fired')

        if kwargs not in self.custom_switch_handler_queue:
            self.custom_switch_handler_queue.append(kwargs)

        self.info_log(self.custom_switch_handler_queue)

    def play_queue_events(self, **kwargs):
        self.info_log('play_queue_events')

        if self.queue_callback_handler:
            self.clear_callback_handler()

        self.custom_switch_handler_queue.sort(key=lambda y: y.get('priority'))

        if self.custom_switch_handler_queue == []:
            self.info_log('queue_is_done')
            self.event_queue_complete()
        else:
            self.current_queue_event = self.custom_switch_handler_queue.pop()
            self.play_current_queue_event()

    def clear_callback_handler(self):
        self.info_log('clear_callback_handler')

        self.machine.events.remove_handler_by_key(self.queue_callback_handler)
        self.queue_callback_handler = None

    def play_current_queue_event(self):
        self.info_log('play_current_queue_event')

        if self.current_queue_event:
            self.queue_callback_handler = self.machine.events.add_handler(
                self.current_queue_event['wait_for'],
                self.play_queue_events
            )

            self.machine.events.post(self.current_queue_event['post'])
        else:
            event_queue_complete()

    def event_queue_complete(self):
        self.info_log("event_queue_complete")

        self.machine.events.post('cmd_mangna_vuk_queue_complete')

        self.fire_vuk()

    def enable(self, **kwargs):
        del kwargs

        if self.enabled:
           return

        self.info_log('Enabling')

        self.delay.remove('ball_clear')

        self.add_vuk_handler()

        self.machine.events.add_handler(
            'cmd_magnavuk_firing', self.enable_magnet)
        self.machine.events.add_handler(
            'magnavuk_magnet_disabled', self.choose_lane)

        self.enabled = True

    def disable(self, **kwargs):
        del kwargs

        self.info_log('Disabling')

        self.remove_auto_vuk_handler()
        self.machine.events.remove_handler_by_event(
            'cmd_magnavuk_firing', self.enable_magnet)
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

        if self.machine.switch_controller.is_active(self.s_jump_ball_vuk_switch):
            self.clear_ball()
        else:
            self.disable()


    def add_vuk_handler(self):
        self.info_log('Add handler')
        self.machine.switch_controller.add_switch_handler(
            's_jump_ball_vuk', self.play_queue_events, 1, 500)

    def remove_auto_vuk_handler(self):
        self.info_log('remove_auto_vuk_handler')
        self.machine.switch_controller.remove_switch_handler(
            's_jump_ball_vuk', self.play_queue_events, 1, 500)
 

    def fire_vuk(self, **kwargs):
        self.info_log('Vuk firing')

        self.machine.events.post('cmd_magnavuk_firing')
        self.machine.coils['c_jump_ball_vuk'].pulse()

    def disable_magnet(self, **kwargs):
        del kwargs

        self.info_log('magnet disabled')
        self.machine.coils['c_jump_ball_magnet'].disable()
        self.machine.events.post('magnavuk_magnet_disabled')

    def choose_lane(self, **kwargs):
        del kwargs

        if self.machine.variables.get_machine_var('magnavuk_left'):
            self.ramp_left()
        else:
            self.ramp_right()

    def enable_magnet(self, **kwargs):
        del kwargs

        self.info_log('magnet enabled')
        self.machine.coils['c_jump_ball_magnet'].enable()
        self.delay.add(500, self.disable_magnet)

    def set_direction(self, direction):
        self.machine.set_machine_var('magnavuk_left', direction == 'left')

    def ramp_left(self):
        self.info_log('ramp_left')
        self.machine.events.post('magnavuk_shot_left')
        self.machine.coils['c_jump_ball_right_kicker'].pulse()

    def ramp_right(self):
        self.info_log('ramp_right')
        self.machine.events.post('magnavuk_shot_right')
        self.machine.coils['c_jump_ball_top_kicker'].pulse()
