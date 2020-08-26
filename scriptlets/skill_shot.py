from mpf.core.custom_code import CustomCode

class SkillShot(CustomCode):
    SHOOTING="shooting"
    BASKET_MADE="basket_made"
    ATTEMPTING_SUPER_SKILL_SHOT="attempting_super_skill_shot"
    SUPER_SKILL_SHOT_AWARDED="super_skill_shot_awarded"

    def on_load(self):
        self.reset()
        self.machine.events.add_handler('cmd_start_skillshot', self.start_skillshot)

    def start_skillshot(self, **kwargs):
        del kwargs

        self.reset()

        self.add_event_handlers()
        self.set_choices()
        self.begin_timer()

    def add_event_handlers(self):
        self.machine.events.add_handler('timer_skill_shot_timer_tick', self.on_skill_shot_timer_tick)
        self.machine.events.add_handler('s_skill_shot_basket_active', self.on_skill_shot_basket_active)
        self.machine.events.add_handler('cmd_playfield_active', self.on_playfield_active)
        self.machine.events.add_handler(
                'timer_skill_shot_success_timer_complete', self.on_skill_shot_success_timer_complete)
        self.machine.events.add_handler(
                'timer_skill_shot_deactivation_timer_complete', self.on_skill_shot_deactivation_timer_complete)
        self.machine.events.add_handler('left_ramp_hit', self.on_super_skill_shot_made)
        self.machine.events.add_handler('cmd_cancel_skill_shot', self.on_cancel_skill_shot)

    def remove_event_handlers(self):
        self.machine.events.remove_handler_by_event('timer_skill_shot_timer_tick', self.on_skill_shot_timer_tick)
        self.machine.events.remove_handler_by_event('s_skill_shot_basket_active', self.on_skill_shot_basket_active)
        self.machine.events.remove_handler_by_event('cmd_playfield_active', self.on_playfield_active)
        self.machine.events.remove_handler_by_event(
                'timer_skill_shot_success_timer_complete', self.on_skill_shot_success_timer_complete)
        self.machine.events.remove_handler_by_event(
                'timer_skill_shot_deactivation_timer_complete', self.on_skill_shot_deactivation_timer_complete)
        self.machine.events.remove_handler_by_event('left_ramp_hit', self.on_super_skill_shot_made)
        self.machine.events.remove_handler_by_event('cmd_cancel_skill_shot', self.on_cancel_skill_shot)

    def on_skill_shot_timer_tick(self, **kwargs):
        self.current_choice = list(self.skill_shot_choices)[kwargs['ticks']]
        self.show_slide()

    def on_skill_shot_basket_active(self, **kwargs):
        if self.is_shooting():
            self.machine.events.post('cmd_stop_projector_loop')
            self.machine.events.post('cmd_light_super_skill_shot')
            self.machine.events.post('cmd_play_film_reel_stop_sound')
            self.state = self.BASKET_MADE
            self.timer.stop()

    def is_shooting(self):
        return self.state == self.SHOOTING

    def plunger_basket_made(self):
        return self.state == self.BASKET_MADE

    def attempting_super_skill_shot(self):
        return self.state == self.ATTEMPTING_SUPER_SKILL_SHOT

    def on_cancel_skill_shot(self, **kwargs):
        if self.attempting_super_skill_shot() == True:
            self.deactivate()

    def on_skill_shot_success_timer_complete(self, **kwargs):
        self.deactivate()

    def on_skill_shot_deactivation_timer_complete(self, **kwargs):
        self.deactivate()

    def on_playfield_active(self, **kwargs):
        if self.timer:
            self.timer.stop()

        if self.state != self.SUPER_SKILL_SHOT_AWARDED:
            if self.plunger_basket_made():
                self.state = self.ATTEMPTING_SUPER_SKILL_SHOT
                self.begin_success_timer()
            elif self.attempting_super_skill_shot() != True:
                self.deactivate()

    def on_super_skill_shot_made(self, **kwargs):
        if self.attempting_super_skill_shot():
            self.state = self.SUPER_SKILL_SHOT_AWARDED
            self.success_timer.stop()
            self.machine.events.post('cmd_play_super_skill_shot_success', award=self.current_choice)
            self.machine.events.post('cmd_skill_shot_show_award_' + self.current_choice)
            self.machine.events.post('cmd_super_skill_shot_award_' + self.current_choice)
            self.machine.events.post('cmd_play_super_skill_shot_slide_background_sound')
            self.begin_deactivation_timer()

    def reset(self):
        try:
            self.timer.stop()
        except AttributeError:
            self.info_log('noop')

        try:
            self.success_timer.stop()
        except AttributeError:
            self.info_log('noop')

        try:
            self.deactivation_timer.stop()
        except AttributeError:
            self.info_log('noop')

        self.state = self.SHOOTING
        self.timer = None
        self.success_timer = None
        self.deactivation_timer = None

    def deactivate(self):
        self.reset()
        self.remove_event_handlers()
        self.machine.events.post('cmd_stop_projector_loop')
        self.machine.events.post('cmd_skill_shot_complete')

    def show_slide(self):
        self.machine.events.post('cmd_play_skill_shot_slide_' + self.current_choice)

    def set_choices(self):
        choices = {
            "light_lock": "Light Lock",
            "extra_ball": "Extra Ball", # written
            "mystery_meat": "Light Mystery Meat", # written
            "one_million": "One Million Points", # written
            "ball_save": "+20 second Ballsave",
            "add_help": "Add Help Letter", # written
            "van": "Light Gas Station",
            "five_million": "Five Million Points", # written
        }

        # Add some conditional choices here

        self.skill_shot_choices = choices


    def begin_timer(self):
        self.timer = self.machine.timers.skill_shot_timer

        self.timer.restart_on_complete = True
        self.timer.set_tick_interval(self.tick_interval())
        self.timer.ticks = 0
        self.timer.start_value = 0
        self.timer.end_value = len(self.skill_shot_choices)
        self.timer.start()

    def begin_success_timer(self):
        self.success_timer = self.machine.timers.skill_shot_success_timer

        self.success_timer.restart_on_complete = False
        self.success_timer.set_tick_interval(1)
        self.success_timer.ticks = 0
        self.success_timer.start_value = 0
        self.success_timer.end_value = 10
        self.success_timer.start()

    def begin_deactivation_timer(self):
        self.deactivation_timer = self.machine.timers.skill_shot_deactivation_timer

        self.deactivation_timer.restart_on_complete = False
        self.deactivation_timer.set_tick_interval(1)
        self.deactivation_timer.ticks = 0
        self.deactivation_timer.start_value = 0
        self.deactivation_timer.end_value = 2
        self.deactivation_timer.start()

    def tick_interval(self):
        tick_interval = 0.3

        return tick_interval
