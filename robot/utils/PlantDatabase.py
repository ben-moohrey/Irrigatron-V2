import json
import os
import time

class PlantDatabase:
    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        self.load()


    def set_is_watered(self, id: int, val: bool):
        if (id is None):
            plants = self.get_plants()
            for i in range(0, len(plants)):
                plants[i]['is_watered'] = False
            self.set_plants(plants)
                
        else:
            p = self.get_plant(id)
            if (p is not None):
                p['is_watered'] = val
                self.set_plant(id, p)

    def reset_is_watered(self, id = None | int):
        if (id is None):
            plants = self.get_plants()
            for i in range(0, len(plants)):
                plants[i]['is_watered'] = False
            self.set_plants(plants)
                
        else:
            p = self.get_plant(id)
            if (p is not None):
                p['is_watered'] = False
                self.set_plant(id, p)
                

        

    def get_needs_watering(self) -> list:
        return list(filter(lambda p: not p['is_watered'], self.get_plants()))


    def set_plant(self, id: int, plant_dict: dict):
        if (self.get_plant(id) is not None):
            self.data['plants'][id] = plant_dict

    def set_plants(self, plants: list):
        self.set('plants', plants)

    def get_plant(self, id: int, default=None):
        """ Return the plant with the given aruco_code or default if not found. """
        plants = self.get_plants()
        for plant in plants:
            if plant['aruco_code'] == id:
                return plant
        return default

    def get_plants(self):
        return self.get('plants')

    def load(self):
        """ Load data from a JSON file. If the file does not exist, initialize with an empty dictionary. """
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                self.data = json.load(file)
        else:
            self.data = {}

    def get(self, key, default=None):
        """ Get the value from database by key, return default if key does not exist. """
        return self.data.get(key, default)

    def set(self, key, value):
        """ Set the value in the database for the given key. """
        self.data[key] = value

    def save(self):
        """ Save the current data to the JSON file. """
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def delete(self, key):
        """ Delete a key from the database. """
        if key in self.data:
            del self.data[key]

    def __str__(self):
        """ Return a string representation of the database for debugging. """
        return json.dumps(self.data, indent=4)

# Example usage
if __name__ == "__main__":
    db = PlantDatabase('/home/irrigatron/Irrigatron-V2/robot/data/database.json')
    db.set('test_key', time.time())
    print(db)  # Print current state of database
    db.save()  # Save to file
