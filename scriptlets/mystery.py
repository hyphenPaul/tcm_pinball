from mpf.core.custom_code import CustomCode
import random

class Mystery(CustomCode):
    def on_load(self):
        self.info_log('Enabling')
        self.machine.events.add_handler('cmd_get_mystery', self.get_mystery)

    def get_mystery(self, **kwargs):
        del kwargs

        self.info_log('Getting Mystery')

        choices = self.fetch_choices()
        self.trace("choices")
        self.info_log(choices)

        choice = random.choice(choices)
        self.machine.game.player["v_current_mystery_value"] = choice
        self.save_acquired_mysteries(choice)

        self.trace("choice")
        self.info_log(choice)

        self.machine.events.post('cmd_mystery_choice', choice=choice)

    def fetch_choices(self):
        choices = []
        frequenies = {
            "small_points": 20, # done score.yaml
            "add_bonus_multiplier": 20,
            "award_chain_saw_letter": 20, # function to determine qualifier
            "light_lock": 20, # function to determine qualifier
            "award_franklin_letter": 20, # function to determine qualifier
            "2_x_playfield": 10,
            "save_from_the_grave": 10,
            "30_second_ball_save": 10,
            "big_points": 10, # done score.yaml
            "jack_shit": 10,
            "award_tilt_warning": 5,
            "light_extra_ball": 5,
            "franklin_frenzy": 1
        }

        for choice, number in frequenies.items():
            for _ in range(number):
                choices.append(choice)

        return self.filter_acquired_choices(choices)


    def filter_acquired_choices(self, choices):
        checked = choices.copy()

        for acquired_choice in self.get_player_acquired_mysteries():
            checked = list(filter((acquired_choice).__ne__, checked))

        if checked == []:
            collected_mysteries = self.get_player_acquired_mysteries()
            self.machine.game.player["collected_mysteries"] = []
            return choices

        return self.filter_choice_by_state(checked)

    def filter_choice_by_state(self, checked):
        rejects = []

        rejections = {
            "award_chain_saw_letter": self.should_reject_saw_letter,
            "light_lock": self.should_reject_saw_letter,
            "award_franklin_letter": self.should_reject_franklin_letter,
            "2_x_playfield": self.should_reject_2_x_playfield,
            "light_extra_ball": self.should_reject_light_extra_ball,
            "franklin_frenzy": self.should_reject_franklin_frenzy
        }

        for choice, reject_func in rejections.items():
            if reject_func():
                rejects.append(choice)

        for reject in rejects:
            checked = list(filter((reject).__ne__, checked))

        return checked

    def should_reject_saw_letter(self):
        return False

    def should_reject_saw_letter(self):
        return False

    def should_reject_franklin_letter(self):
        return False

    def should_reject_2_x_playfield(self):
        return False

    def should_reject_light_extra_ball(self):
        return False

    def should_reject_franklin_frenzy(self):
        return False

    def save_acquired_mysteries(self, mystery):
        if self.ensure_player_acquired_mysteries():
            collected_mysteries = self.get_player_acquired_mysteries()
            collected_mysteries.append(mystery)
            unique_choices = self.uniqify(collected_mysteries)
            collected_mysteries = unique_choices

    def ensure_player_acquired_mysteries(self):
        player = self.machine.game.player

        if not player:
            return False

        if player["collected_mysteries"] != 0:
            return True

        player["collected_mysteries"] = []

        return True

    def get_player_acquired_mysteries(self):
        player = self.machine.game.player

        if self.ensure_player_acquired_mysteries():
            return player["collected_mysteries"]

        return []

    def trace(self, str):
        padding = 25 * "*"
        self.info_log(padding + " " + str + " " +  padding)

    def uniqify(self, seq):
       checked = []

       for e in seq:
           if e not in checked:
               checked.append(e)
           return checked
