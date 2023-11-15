from mpf.core.custom_code import CustomCode

class WeaponSlides(CustomCode):
    import time

    def on_load(self):
        self.info_log("Enabling")

        self.slide_names = [
            "knife",
            "nunchucks",
            "axe",
            "shotgun",
            "flamethrower",
            "chainsaw"
        ]
        self.bonus_slides = []

        self.machine.events.add_handler("cmd_finalbattle_show_initial_bonus_slide", self.show_initial_bonus_slide)
        self.machine.events.add_handler("ball_save_finalbattle_phase_1_saving_ball", self.show_bonus_slides)
        self.machine.events.add_handler("timer_finalbattle_bonus_timer_tick", self.show_slides)
        self.machine.events.add_handler("cmd_finalbattle_bonus_slides_completed", self.on_slides_complete)

    def collected_slides(self):
        collected = []
        current_player = self.current_player()

        for slide_name in self.slide_names:
            if current_player["v_finalbattle_" + slide_name + "_collected"] == 1:
                collected.append(slide_name)

        return collected

    def show_initial_bonus_slide(self, **kwargs):
        self.machine.events.post("cmd_finalbattle_bonus_intro_slide")

    def show_bonus_slides(self, **kwargs):
        self.bonus_slides = self.all_slides()
        self.bonus_slides.reverse()
        self.machine.events.post("cmd_finalbattle_bonus_timer_restart")

    def show_slides(self, **kwargs):
        if self.bonus_slides == []:
            self.machine.events.post("cmd_finalbattle_bonus_slides_completed")
            self.machine.events.post("cmd_finalbattle_bonus_timer_stop")
        else:
            slide = self.bonus_slides.pop()
            self.machine.events.post("cmd_finalbattle_play_" + slide + "_collect_sound")
            self.machine.events.post("cmd_finalbattle_play_" + slide + "_brad_sound")
            self.machine.events.post("cmd_finalbattle_bonus_" + slide + "_slide")

    def on_slides_complete(self, **kwargs):
        self.machine.events.post("cmd_remove_finalbattle_bonus_intro_slide")
        self.machine.events.post("cmd_finalbattle_bonus_slides_complete")

    def all_slides(self):
        collected = self.collected_slides()

        if len(collected) == len(self.slide_names):
            self.machine.events.post("cmd_finalbattle_score_collect_all_weapons")
            collected.append("fully_loaded")

        if collected == []:
            collected.append("nothing")

        return collected


    def current_player(self):
        return self.machine.game.player
