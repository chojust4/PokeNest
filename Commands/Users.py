# User and Users class

# Users class to store the guild users
class Users:
    def __init__(self):
        self.users = {}

    # Add user into the list of users
    def add(self, user):
        if user not in self.users.values():
            self.users[user.user_id] = user
        else:
            return


# User class to store the unique user and their respective pokemon in the guild
# Each user has a collection of Pokemon
class User:
    def __init__(self, user_id, pokemon):
        self.pokemon = pokemon
        self.user_id = user_id
        self.user_collection = {self.pokemon.name: self.pokemon}
        self.selected_pokemon = None

    # Add pokemon to users collection
    def add(self, pokemon):
        self.user_collection[pokemon.name] = pokemon

    # Remove pokemon from users collection if it exists
    def remove(self, pokemon):
        if pokemon not in self.user_collection:
            return
        else:
            del self.user_collection[pokemon.name]

    # Select pokemon
    def select_pokemon(self, pokemon_name):
        pokemon = self.user_collection.get(pokemon_name)
        self.selected_pokemon = pokemon
