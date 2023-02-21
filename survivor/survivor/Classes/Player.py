class Player:
    """ 
        Player Class 
    
    """
    def __init__ (self, login, password, is_admin):
        self.login = login
        self.password = password
        self.is_admin = is_admin
        self.tribe = None
        self.idol_count = 0
        self.is_immune = False
        self.is_still_playing = True

    def set_name(self, name):
        self.name = name

    def set_avatar(self, img_url):
        self.avatar = img_url
    
    def set_discord(self, discord):
        self.discord = discord

    def set_bio(self):
        pass

    def change_tribe(self, Tribe):
        self.tribe = Tribe

    def set_immunity(self, is_immune):
        self.is_immune = is_immune

    def eliminate_player(self):
        self.is_still_playing = False

    def add_idol(self):
        self.idol_count += 1

    def use_idol(self):
        if self.idol_count >= 1:
            self.idol_count -= 1

    def give_idol(self, Player_given_idol):
        if self.idol_count >= 1:
            self.idol_count -= 1
            Player_given_idol.add_idol()