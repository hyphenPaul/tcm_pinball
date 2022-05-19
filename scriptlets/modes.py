from mpf.core.custom_code import CustomCode

class Modes(CustomCode):
    def on_load(self):
        self.initiated = False
        self.enabled = False
        self.info_log('Enabling')

        self.modes = {
            "hitchhiker" :  { "light" : "grid_in_yer_face", "mode_name" : "hitchhiker" },
            "barbecue" :  { "light" : "grid_fire", "mode_name" : "barbecue" },
            "grandpa" :  { "light" : "grid_space_jam", "mode_name" : "grandpa" },
            "grave" :  { "light" : "grid_slam", "mode_name" : "grave" },
            "sally" :  { "light" : "grid_fastbreak", "mode_name" : "sally" },
            "sawemall" :  { "light" : "grid_rebound", "mode_name" : "sawemall" }
#            "sawemall1" :  { "light" : "grid_rebound", "mode_name" : "sawemall" },
#            "sawemall2" :  { "light" : "grid_space_jam", "mode_name" : "sawemall" },
#            "sawemall3" :  { "light" : "grid_in_yer_face", "mode_name" : "sawemall" },
#            "sawemall4" :  { "light" : "grid_slam", "mode_name" : "sawemall" },
#            "sawemall5" :  { "light" : "grid_fire", "mode_name" : "sawemall" }
        }

        self.machine.events.add_handler('mode_base_started', self.init_on_ball_start)
        self.machine.events.add_handler('cmd_enable_mode_switcher', self.on_enable)
        self.machine.events.add_handler('cmd_disable_mode_switcher', self.on_disable)
        self.machine.events.add_handler('cmd_super_skill_shot_award_van', self.on_skill_shot)
        self.machine.events.add_handler('game_ending', self.on_game_ending)

    def init_on_ball_start(self, **kwargs):
        self.initiated = True
        self.enable()

    def on_game_ending(self, **kwargs):
        self.clear_current_collected_modes()

    def enable(self):
        self.info_log('enable')

        if self.enabled == False:
            self.enabled = True
            self.machine.events.add_handler('drop_target_bank_van_down', self.on_drop_target)
            self.machine.events.add_handler('s_left_slingshot_active', self.cycle_mode)
            self.machine.events.add_handler('s_right_slingshot_active', self.cycle_mode)
            self.reset_van_drop_targets()
            self.refresh()

    def disable(self):
        self.info_log('disable')
        self.enabled = False
        self.machine.events.post('cmd_disable_bh_mode_van')
        self.machine.events.remove_handler_by_event('drop_target_bank_van_down', self.on_drop_target)
        self.machine.events.remove_handler_by_event('s_left_slingshot_active', self.cycle_mode)
        self.machine.events.remove_handler_by_event('s_right_slingshot_active', self.cycle_mode)
        self.machine.events.remove_handler_by_event('ball_hold_bh_mode_van_full', self.on_van_vuk)
        self.turn_off_all_lights()

    def on_enable(self, **kwargs):
        self.enable()

    def on_disable(self, **kwargs):
        self.disable()

    def turn_off_all_lights(self):
        self.info_log('turn_off_all_lights')
        # playfield lights
        for mode in self.modes:
            self.machine.lights[self.modes[mode]["light"]].off()

        self.stop_flash_lights()

    def refresh(self):
        self.info_log('refresh')

        if not self.initiated:
            self.info_log('refresh not initiated')
            return

        current_player = self.current_player()

        for mode in self.modes:
            if mode in self.current_collected_modes():
                self.machine.lights[self.modes[mode]["light"]].on()
            else:
                self.machine.lights[self.modes[mode]["light"]].off()

        self.stop_flash_lights()
        self.machine.events.remove_handler_by_event('ball_hold_bh_mode_van_full', self.on_van_vuk)

        if self.current_active_mode():
            self.info_log('refresh active mode')
            current_player['v_active_mode_light'] = self.modes[self.current_active_mode()]["light"]

            if self.is_mode_active():
                self.flash_light()
                self.add_van_vuk_listeners()
                self.start_shoot_the_van_show()
            else:
                self.pulse_light()
        else:
            self.info_log('refresh no active mode')

    def available_for_skillshot(self):
        if self.is_mode_active():
            return False

        if self.current_active_mode():
            return True
        else:
            return False

    def on_skill_shot(self, **kwargs):
        self.set_mode_is_active()
        self.refresh()

    def reset_van_ball_hold(self):
        self.machine.events.remove_handler_by_event('ball_hold_bh_mode_van_full', self.on_van_vuk)
        self.machine.events.post('cmd_reset_bh_mode_van')
        self.machine.events.post('cmd_enable_bh_mode_van')

    def disable_base_vuk_messaging(self):
        self.machine.events.post('cmd_disable_light_van_message')

    def add_van_vuk_listeners(self):
        self.reset_van_ball_hold()
        self.disable_base_vuk_messaging()
        self.machine.events.add_handler('ball_hold_bh_mode_van_full', self.on_van_vuk)

    def on_van_vuk(self, **kwargs):
        self.info_log('on_vuk')
        self.machine.events.remove_handler_by_event('ball_hold_bh_mode_van_full', self.on_van_vuk)
        self.machine.events.post('cmd_disable_bh_mode_van')
        self.machine.events.post('cmd_score_start_mode')
        self.collect_current_mode()
        self.machine.events.post('cmd_start_' + self.modes[self.current_active_mode()]["mode_name"] + '_mode')
        self.set_mode_is_inactive()
        self.reset_van_drop_targets()
        self.disable()

    def start_shoot_the_van_show(self):
        self.machine.events.post('cmd_start_shoot_the_van')

    def reset_van_drop_targets(self):
        self.machine.events.post('cmd_reset_van_drop_targets')

    def cycle_mode(self, **kwargs):
        self.info_log('cycle_mode')

        if self.is_mode_active():
            return

        current_player = self.current_player()

        if self.current_active_mode():
            current_index = self.remaining_modes().index(self.current_active_mode())

            if current_index + 1 >= len(self.remaining_modes()):
                current_player['v_current_active_mode'] = self.remaining_modes()[0]
            else:
                current_player['v_current_active_mode'] = self.remaining_modes()[current_index + 1]

            self.refresh()

    def stop_flash_lights(self):
        self.machine.events.post('cmd_stop_flash_mode_lights')

    def pulse_light(self):
        self.machine.events.post('cmd_pulse_mode_light')

    def flash_light(self):
        self.machine.events.post('cmd_flash_mode_light_' + self.current_player()['v_active_mode_light'])

    def on_drop_target(self, **kwargs):
        if not self.initiated:
            return

        if self.is_mode_active():
            return

        self.set_mode_is_active()
        self.refresh()

    def set_mode_is_active(self):
        current_player = self.current_player()
        current_player['v_mode_is_active'] = True

    def set_mode_is_inactive(self):
        current_player = self.current_player()
        current_player['v_mode_is_active'] = False
        current_player['v_current_active_mode'] = None


    def is_mode_active(self):
        current_player = self.current_player()

        if current_player['v_mode_is_active'] is None:
            current_player['v_mode_is_active'] = False

        return current_player['v_mode_is_active']

    def mode_list(self):
        return self.modes.keys()

    def remaining_modes(self):
        return list(set(self.mode_list()) - set(self.current_collected_modes()))

    def collect_current_mode(self):
        current_player = self.current_player()

        if self.current_active_mode() not in self.current_collected_modes():
            current_player['v_collected_modes'].append(self.current_active_mode())

    def current_collected_modes(self):
        current_player = self.current_player()

        if current_player['v_collected_modes']:
            return current_player['v_collected_modes']
        else:
            current_player['v_collected_modes'] = []
            return []

    def clear_current_collected_modes(self):
        current_player = self.current_player()
        current_player['v_collected_modes'] = []

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
