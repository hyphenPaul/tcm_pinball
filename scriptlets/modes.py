from mpf.core.custom_code import CustomCode

class Modes(CustomCode):
    def on_load(self):
        self.initiated = False
        self.info_log('Enabling')

        self.modes = {
            "a" :  { "light" : "grid_in_yer_face" },
            "b" :  { "light" : "grid_fire" },
            "c" :  { "light" : "grid_space_jam" },
            "d" :  { "light" : "grid_rebound" },
            "e" :  { "light" : "grid_slam" },
            "f" :  { "light" : "grid_fastbreak" }
        }

        self.machine.events.add_handler('mode_base_started', self.init_on_ball_start)
        self.machine.events.add_handler('drop_target_bank_van_down', self.on_drop_target)
        self.machine.events.add_handler('s_left_slingshot_active', self.cycle_mode)
        self.machine.events.add_handler('s_right_slingshot_active', self.cycle_mode)

    def init_on_ball_start(self, **kwargs):
        self.initiated = True
        self.refresh_lights()

    def refresh_lights(self):
        self.info_log('refresh_lights')

        if not self.initiated:
            self.info_log('refresh_lights not initiated')
            return

        current_player = self.current_player()

        for mode in self.modes:
            if mode in self.current_collected_modes():
                self.machine.lights[self.modes[mode]["light"]].on()
            else:
                self.machine.lights[self.modes[mode]["light"]].off()

        self.stop_flash_lights()

        if self.current_active_mode():
            self.info_log('refresh_lights active mode')
            current_player['v_active_mode_light'] = self.modes[self.current_active_mode()]["light"]

            if self.mode_is_active():
                self.flash_light()
            else:
                self.pulse_light()
        else:
            self.info_log('refresh_lights no active mode')

    def cycle_mode(self, **kwargs):
        self.info_log('cycle_mode')

        current_player = self.current_player()

        if current_player['v_mode_is_active']:
            return

        if self.current_active_mode():
            current_index = self.remaining_modes().index(self.current_active_mode())

            if current_index + 1 >= len(self.remaining_modes()):
                current_player['v_current_active_mode'] = self.remaining_modes()[0]
            else:
                current_player['v_current_active_mode'] = self.remaining_modes()[current_index + 1]

            self.refresh_lights()

    def stop_flash_lights(self):
        self.machine.events.post('cmd_stop_flash_mode_light')

    def pulse_light(self):
        self.machine.events.post('cmd_pulse_mode_light')

    def flash_light(self):
        self.machine.events.post('cmd_flash_mode_light_' + self.current_player()['v_active_mode_light'])

    def on_drop_target(self, **kwargs):
        if not self.initiated:
            return

        current_player = self.current_player()

        current_player['v_mode_is_active'] = True

        self.refresh_lights()

    def mode_is_active(self):
        current_player = self.current_player()

        if current_player['v_mode_is_active'] is None:
            current_player['v_mode_is_active'] = False
            
        return current_player['v_mode_is_active']

    def mode_list(self):
        return self.modes.keys()

    def remaining_modes(self):
        return list(set(self.mode_list()) - set(self.current_collected_modes()))

    def current_collected_modes(self):
        current_player = self.current_player()

        if current_player['v_collected_modes']:
            return current_player['v_collected_modes']
        else:
            current_player['v_collected_modes'] = []
            return []

    def current_active_mode(self):
        current_player = self.current_player()

        if current_player['v_current_active_mode']:
            return current_player['v_current_active_mode']
        else:
            try:
                mode = self.remaining_modes()[0]
                current_player['v_current_active_mode'] = mode

                return mode
            except IndexError:
                return None

    def current_player(self):
        return self.machine.game.player
