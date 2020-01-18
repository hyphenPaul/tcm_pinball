from mpf.core.custom_code import CustomCode

class SkillShot(CustomCode):

    def on_load(self):
        self.reset()
        self.machine.events.add_handler('cmd_start_skillshot', self.start_skillshot)

    def start_skillshot(self, **kwargs):
        del kwargs

        self.reset()
        self.choosing = True

        self.add_event_handlers()
        self.set_choices()
        self.begin_timer()

    def add_event_handlers(self):
        self.machine.events.add_handler('timer_skill_shot_timer_tick', self.on_skill_shot_timer_tick)
        self.machine.events.add_handler('s_skill_shot_basket_active', self.on_skill_shot_basket_active)
        self.machine.events.add_handler('playfield_active', self.on_playfield_active)
        self.machine.events.add_handler('timer_skill_shot_success_timer_complete', self.on_skill_shot_success_timer_complete)

    def on_skill_shot_timer_tick(self, **kwargs):
        self.current_choice = list(self.skill_shot_choices)[kwargs['ticks']]
        self.show_slide()

    def on_skill_shot_basket_active(self, **kwargs):
        if self.choosing:
            self.successful_basket = True
            self.timer.stop()
            
        self.choosing = False

    def on_skill_shot_success_timer_complete(self, **kwargs):
        self.deactivate()

    def on_playfield_active(self, **kwargs):
        self.timer.stop()

        if self.successful_basket:
            self.info_log('shp successful')
            self.begin_success_timer()
        else:
            self.info_log('shp unsuccessful')
            self.deactivate()

        self.successful_basket: False

    def reset(self):
        try:
            self.timer.stop()
        except AttributeError:
            self.info_log('noop')

        try:
            self.begin_success_timer.stop()
        except AttributeError:
            self.info_log('noop')

        self.choosing = False
        self.timer = None
        self.success_timer = None
        self.successful_basket = False

    def deactivate(self):
        self.reset()
        self.machine.events.post('cmd_stop_skill_shot_mode')

    def show_slide(self):
        self.machine.events.post('cmd_play_skill_shot_slide_' + self.current_choice)

    def set_choices(self):
        choices = {
            "big_points": "Big Points",
            "little_points": "Little Points",
            "extended_ball_save": "Extended Ball Save",
            "help": "Award Help",
            "light_gas_station": "Light Gas Station"
        }

        #"light_extra_ball": "Light Extra Ball",
        #"light_lock": "Light Lock",
        #"light_mystery": "Light Mystery"

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
        self.success_timer.set_tick_interval(self.tick_interval())
        self.success_timer.ticks = 0
        self.success_timer.start_value = 0
        self.success_timer.end_value = 6
        self.success_timer.start()

    def tick_interval(self):
        tick_interval = 0.5

        return tick_interval
