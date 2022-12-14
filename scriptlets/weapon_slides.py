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

        self.machine.events.add_handler("cmd_finalbattle_show_bonus_slides", self.show_bonus_slides)
        self.machine.events.add_handler("timer_finalbattle_bonus_timer_tick", self.show_slides)

    def collected_slides(self):
        collected = []
        current_player = self.current_player()

        for slide_name in self.slide_names:
            if current_player["v_finalbattle_" + slide_name + "_collected"] == 1:
                collected.append(slide_name)

        return collected

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
            self.machine.events.post("cmd_" + slide)


    def all_slides(self):
        collected = self.collected_slides()

        if len(collected) == len(self.slide_names):
            collected.append("fully_loaded")

        if collected == []:
            collected.append("nothing")

        collected = ["intro"] + collected

        final = []

        for name in collected:
            final.append("finalbattle_bonus_" + name + "_slide")

        return final


    def current_player(self):
        return self.machine.game.player
