from mpf.core.custom_code import CustomCode

class Magnavuk(CustomCode):

    def on_load(self):
        self.info_log('Loading')

        self.enabled = False
        self.current_custom_switch_handler = None
        self.auto_fire = self.machine.get_machine_var('magnavuk_auto_fire')

        if self.machine.switch_controller.is_active('s_jump_ball_vuk'):
            self.delay.add(1000, self.clear_ball)

        self.machine.events.add_handler('ball_started', self.enable)
        self.machine.events.add_handler('ball_ended', self.disable)
        self.machine.events.add_handler('cmd_custom_magna_vuk_handler', self.add_custom_vuk_handler)
        self.machine.events.add_handler('cmd_mangna_vuk_reset_auto_handler', self.reset_auto_vuk_handler)

        # handler queue
        self.custom_switch_handler_queue = []
        self.machine.events.add_handler('cmd_custom_magna_vuk_queue_event', self.add_queue_event)
        self.machine.events.add_handler('cmd_play_magna_vuk_queue', self.play_queue_events)
        self.current_queue_event = None
        self.queue_callback_handler = None

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
        self.machine.events.remove_handler_by_key(self.queue_callback_handler)
        self.queue_callback_handler = None
            
 
    def play_current_queue_event(self):
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

    def enable(self, **kwargs):
        del kwargs

        if self.enabled:
           return

        self.info_log('Enabling')

        self.delay.remove('ball_clear')

        if self.auto_fire:
            self.add_auto_vuk_handler()

        self.machine.events.add_handler(
            'cmd_magnavuk_firing', self.enable_magnet)
        self.machine.events.add_handler(
            'magnavuk_magnet_disabled', self.choose_lane)

        self.enabled = True

        # testing
        self.machine.events.add_handler(
            'cmd_test_queue_event',
            self.test_queue_event,
            priority=10,
            blocking_facility=None,
            kwargs={"post": "cmd_play_test_show_1", "wait_for":"cmd_test_show_1_complete"}
        )

        #self.machine.events.add_handler(
        #    'cmd_test_queue_event',
        #    self.test_queue_event,
        #    priority=9,
        #    blocking_facility=None,
        #    kwargs={"post": "cmd_play_test_show_2", "wait_for":"cmd_test_show_2_complete"}
        #)

        # notes
        # - settings = "the event name"
        # - context = "mode name"
        # - calling_context = "event"

    def test_queue_event(self, **kwargs):

        self.info_log('000')
        self.info_log(self.machine.queue_relay_player.config_file_section) # queue_relay_player
        self.info_log(self.machine.queue_relay_player.instances['test'])
        self.info_log(self.machine.queue_relay_player.validate_config('queue_relay_player'))
        self.info_log('000')

        self.machine.events.post(kwargs['kwargs']['post'])

        self.info_log('****************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************')


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

        if self.machine.switch_controller.is_active('s_jump_ball_vuk'):
            self.clear_ball()
        else:
            self.disable()

    def reset_auto_vuk_handler(self, **kwargs):
        self.remove_auto_vuk_handler()
        self.remove_current_switch_handler()
        self.add_auto_vuk_handler()

    def remove_auto_vuk_handler(self):
        self.info_log('remove_auto_vuk_handler')
        self.machine.switch_controller.remove_switch_handler(
            's_jump_ball_vuk', self.fire_vuk, 1, 500)

    def add_auto_vuk_handler(self, **kwargs):
        self.info_log('Add handler')
        self.machine.switch_controller.add_switch_handler(
            's_jump_ball_vuk', self.fire_vuk, 1, 500)

    def add_custom_vuk_handler(self, **kwargs):
        self.info_log('add_custom_vuk_handler')

        self.remove_auto_vuk_handler()
        self.remove_current_switch_handler()

        self.current_custom_switch_handler = self.machine.switch_controller.add_switch_handler(
            's_jump_ball_vuk', self.handle_custom_vuk_event, 1, 500, False, kwargs)

    def push_custom_vuk_handler(self, **kwargs):
        self.info_log('add_custom_vuk_handler')

        self.remove_current_switch_handler()

        self.current_custom_switch_handler = self.machine.switch_controller.add_switch_handler(
            's_jump_ball_vuk', self.handle_custom_vuk_event, 1, 500, False, kwargs)
        # This may be as easy as just adding events, 

        # Posting queue: http://developer.missionpinball.org/en/dev/api/self.machine.events.html#mpf.core.events.EventManager.post_queue

        # Questions: How do I register a queue event vs regular event


        # Add queue event player that fires the vuk at the end
        # It also removes any items from the queue player
        # 

        # create a function that adds to the relay player
        # it needs to check to make sure it doesn't exist already
        # need to pass the post value (beginngin of show) and the wait_for value (end of the show), the post \
        #   - they all listen to the same event (queue event from the queue event player)

        # how the fuck do you dynamically add a queue event


    def handle_custom_vuk_event(self, **kwargs):
        self.info_log('handle_custom_vuk_event')

        self.info_log('try to remove this handler')
        self.remove_current_switch_handler()

        self.machine.events.add_handler(
            kwargs['fire_vuk_evnt'],
            self.fire_vuk,
            priority=1,
            blocking_facility=None,
            kwargs=kwargs
        )

        self.machine.events.post(kwargs['switch_hit_evnt'])

    def remove_current_switch_handler(self):
        if self.current_custom_switch_handler:
            self.machine.switch_controller.remove_switch_handler_by_key(self.current_custom_switch_handler)
            self.current_custom_switch_handler = None

    def fire_vuk(self, **kwargs):
        if 'kwargs' in kwargs:

            args = kwargs['kwargs']

            if 'fire_vuk_evnt' in args:
                self.machine.events.remove_handler(self.fire_vuk)

                if self.auto_fire:
                    self.add_auto_vuk_handler()

            if 'coil_direction' in args:
                self.set_direction(args['coil_direction'])


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

    def set_direction(self, direction):
        self.machine.set_machine_var('magnavuk_left', direction == 'left')

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
