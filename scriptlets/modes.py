from mpf.core.custom_code import CustomCode

class Modes(CustomCode):
    def on_load(self):
        self.info_log('Enabling')

        self.modes = {
            "a" :  { "light" : "grid_in_yer_face" },
            "b" :  { "light" : "grid_fire" },
            "c" :  { "light" : "grid_space_jam" },
            "d" :  { "light" : "grid_rebound" },
            "e" :  { "light" : "grid_slam" },
            "f" :  { "light" : "grid_fastbreak" }
        }

        self.machine.events.add_handler('cmd_start_modes', self.init_on_ball_start)
        self.machine.events.add_handler('drop_target_bank_van_down', self.on_drop_target)

    def init_on_ball_start(self, **kwargs):
        self.refresh_lights()

    def refresh_lights(self):
        for mode in self.modes:
            if mode in self.current_collected_modes():
                self.machine.lights[self.modes[mode]["light"]].on()
            else:
                self.machine.lights[self.modes[mode]["light"]].off()

        if self.mode_is_active?():
            flash_lights(self.modes[current_active_mode()]["light"]) 

    def flash_lights(self, light):
        self.machine.events.post('cmd_flash_lights', light=light)

    def on_drop_target(self, **kwargs):
        current_player['v_mode_is_active'] = True


    def mode_is_active?(self):
        if current_player['v_mode_is_active'] is None
            current_player['v_mode_is_active'] = False
            return False
        else:
            return current_player['v_mode_is_active']


    def mode_list(self):
        return getList(self.modes)

    def remaning_modes(self):
        return list(set(mode_list()) - set(current_collected_modes()))

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
                mode = remaning_modes()[1]
                current_player['v_current_active_mode'] = mode

                return mode
            except IndexError:
                return None


    def current_player(self):
        return self.machine.game.player
