from mpf.core.custom_code import CustomCode
import random

class Mystery(CustomCode):
    def on_load(self):
        self.info_log('Enabling')
        self.machine.events.add_handler('cmd_get_mystery', self.get_mystery)
        self.machine.events.add_handler('cmd_mystery_award_chainsaw_letter', self.on_award_chainsaw_letter)
        self.machine.events.add_handler('cmd_mystery_light_lock', self.on_light_lock)
        self.machine.events.add_handler('cmd_mystery_franklin_letter', self.on_franklin_letter)
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
            "small_points": 20,
            "add_bonus_multiplier": 20,
            "award_chain_saw_letter": 20,
            "light_lock": 20,
            "award_franklin_letter": 20,
            "2_x_playfield": 10,
            "30_second_ball_save": 10,
            "big_points": 10,
            "jack_shit": 10,
            "award_tilt_warning": 5,
            "light_extra_ball": 1
#            "save_from_the_grave": 10, # on hold
#            "collect_bonus": 10, # on hold
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
        self.info_log(self.machine.shots['left_franklin_shot'].state)
        self.info_log(self.machine.shots['left_franklin_shot'].state_name)
        self.info_log(self.machine.shots['right_franklin_shot'].state)
        self.info_log(self.machine.shots['right_franklin_shot'].state_name)

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
        if not self.is_mode_active("escape"):
            return True

        safe_states = ["start", "lock_1_locked", "lock_2_locked"]
        current_state = self.machine.game.player["v_escape_state"]

        for i in safe_states:
            if(i == current_state) :
                return False

        return True

    def on_light_lock(self, **kwargs):
        self.machine.events.post('cmd_mystery_show_complete')
        self.machine.events.post('cmd_mystery_meat_award_light_lock')

    # Franklin

    def should_reject_franklin_letter(self):
        if not self.is_mode_active("franklin"):
            return True

        (self.machine.shots['left_franklin_shot'].state + self.machine.shots['right_franklin_shot'].state) < 7

    def on_franklin_letter(self, **kwargs):
        if self.machine.shots['left_franklin_shot'].state < 4:
            self.machine.shots['left_franklin_shot'].hit()
        else:
            self.machine.shots['right_franklin_shot'].hit()

    # 2 x playfield

    # TODO: This needs to be updated
    def should_reject_2_x_playfield(self):
        if not self.is_mode_active("tt_playfield"):
            return True

        if self.machine.game.player["v_ttp_enabled"] == 1:
            return True

        if self.machine.game.player["v_tt_playfield_counter_count"] > 2:
            return True

        return False

    def should_reject_light_extra_ball(self):
        return False

    def should_reject_franklin_frenzy(self):
        return False

    def is_mode_active(self, mode_name):
        return self.machine.mode_controller.is_active(mode_name)
