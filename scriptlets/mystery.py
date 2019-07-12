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
        self.save_acquired_mysteries(choice)

        #self.trace("player_acquired_mysteries")
        #self.info_log(self.get_player_acquired_mysteries())

        self.trace("choice")
        self.info_log(choice)

    def fetch_choices(self):
        choices = []
        frequenies = {
            "Small Points": 50,
            "Add Bonus Multiplier": 20,
            "Award Chain Saw letter": 20, # function to determine qualifier
            "Light Lock": 20, # function to determine qualifier
            "Award 1 Franklin Letter": 20, # function to determine qualifier 
            "Save From The Grave": 10,
            "30 second Ball Save": 10,
            "Big Points": 10,
            "Jack Shit": 10,
            "Award Tilt Warning": 5,
            "Light Extra Ball": 5,
            "Franklin Frenzy": 1
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
