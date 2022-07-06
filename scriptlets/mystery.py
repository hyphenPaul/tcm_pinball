from mpf.core.custom_code import CustomCode
import random

class Mystery(CustomCode):
    def on_load(self):
        self.info_log('Enabling')
        self.machine.events.add_handler('cmd_get_mystery', self.get_mystery)
        self.machine.events.add_handler('cmd_mystery_award_chainsaw_letter', self.on_award_chainsaw_letter)
        self.machine.events.add_handler('cmd_mystery_light_lock', self.on_light_lock)
        #self.machine.events.add_handler('s_left_flipper_active', self.flipper_test)

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
#            "small_points": 20, # done
#            "add_bonus_multiplier": 20, # done
#            "award_chain_saw_letter": 20, # function to determine qualifier
            "light_lock": 20, # function to determine qualifier
#            "award_franklin_letter": 20, # function to determine qualifier
#            "2_x_playfield": 10,
#            "save_from_the_grave": 10,
#            "30_second_ball_save": 10,
#            "big_points": 10, # done score.yaml
#            "jack_shit": 10,
#            "award_tilt_warning": 5,
#            "light_extra_ball": 5,
#            "franklin_frenzy": 1
        }

        for choice, number in frequenies.items():
            for _ in range(number):
                choices.append(choice)

        return self.filter_acquired_choices(choices)


    def filter_acquired_choices(self, choices):
        checked = choices.copy()

        for acquired_choice in self.get_player_acquired_mysteries():
            checked = list(filter((acquired_choice).__ne__, checked))

        checked = self.filter_choice_by_state(checked)

        if checked == []:
            collected_mysteries = self.get_player_acquired_mysteries()
            self.machine.game.player["collected_mysteries"] = []
            return self.filter_choice_by_state(choices)

        return checked

    def filter_choice_by_state(self, checked):
        rejects = []

        rejections = {
            "award_chain_saw_letter": self.should_reject_saw_letter,
            "light_lock": self.should_reject_light_lock,
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

    ##################################################
    # Choices Logic
    ##################################################

    # Chainsaw Letter

    def flipper_test(self, **kwargs):
        self.info_log(self.is_mode_active('chainsaw'))

    def should_reject_saw_letter(self):
        if not self.is_mode_active("chainsaw"):
            return True

        return self.current_available_chainsaw_letters() == []

    def current_available_chainsaw_letters(self):
        letters = ["c", "h", "a", "i", "n", "s", "a2", "w"]
        letters_copy = self.chainsaw_letters().copy()
        collected_letters_copy = self.collected_chainsaw_letters().copy()
        result = list(set(letters_copy) - set(collected_letters_copy))
        result.sort(key=self.chainsaw_letter_index)

        return result

    def collected_chainsaw_letters(self):
        letters_copy = self.chainsaw_letters().copy()
        collected_letters = []

        for letter in letters_copy:
            if self.machine.game.player[f'v_chainsaw_{letter}_collected'] == 1:
                collected_letters.append(letter)

        return collected_letters

    def chainsaw_letters(self):
        return ["c", "h", "a", "i", "n", "s", "a2", "w"]

    def chainsaw_letter_index(self, letter):
        return self.chainsaw_letters().index(letter)

    def on_award_chainsaw_letter(self, **kwargs):
        letters = self.current_available_chainsaw_letters()
        letter = letters[0]

        if ['s', 'a2', 'w'].count(letter) == 0:
            self.machine.shots[f'chain_{letter[0]}_shot'].hit()
        else:
            self.machine.shots[f'saw_{letter[0]}_shot'].hit()

    # escape lock

    def should_reject_light_lock(self):
        return False

    def on_light_lock(self):
        # need to stop the vuk and fire it with the escape mode
        self.machine.events.post('cmd_remove_mystery_meat_vuk_event')

        # fire the next lock animation
        # set the appropriate variables and shots in escape

    # Franklin

    def should_reject_franklin_letter(self):
        return False

    def should_reject_2_x_playfield(self):
        return False

    def should_reject_light_extra_ball(self):
        return False

    def should_reject_franklin_frenzy(self):
        return False


    def is_mode_active(self, mode_name):
        return self.machine.mode_controller.is_active(mode_name)
