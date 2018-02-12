import argparse
import json
import os
import random
import copy

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0

ship_size = {"Submarine" : 3,
            "Battleship" : 4,
            "Carrier" : 5,
            "Cruiser" : 3,
            "Destroyer" : 2}

def main(player_key):
    global map_size
    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)
    map_size = state['MapDimension']
    if state['Phase'] == 1:
        place_ships()
    else:
        fire_shot(state['OpponentMap']['Cells'])


def output_shot(x, y):
    move = 1  # 1=fire shot command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass


def fire_shot(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)

    """
        * Randomize the place to shot in a chessboard pattern, prioritize center area first
        * If it hits :
            * If special shots is currentyl available, fire it.
                * For every direction the shot hits, continue along that direction with normal shots.
                * If it hits nothing, target untested direction with normal shots.
                Afterwards, follow normal shots rule.
            * Else,
                * Try to shoot up, down, left, or right (randomized).
                  If it doesn't hit, try another direction.
                  If it hits, continue along that direction until the opponent's ship is destroyed.
    """

    targets = []
    for cell in opponent_map:
        if not cell['Damaged'] and not cell['Missed']:
            valid_cell = cell['X'], cell['Y']
            targets.append(valid_cell)
    target = random.choice(targets)
    output_shot(*target)
    return

def InsertShipIntoMap(cmd,map):
    # Inserting a ship to the dummy map based on the command string
    # cmd is assumed to be valid (please test cmd configuration first with test_ship_placement)
    global ship_size
    ship = (copy.copy(cmd)).split(" ")
    type = ship[0]
    x = int(ship[1])
    y = int(ship[2])
    direct = ship[3]
    for i in range(ship_size[type]):
        if (direct == "north"):
            map[y + i][x] = 'X'
        elif (direct == "east"):
            map[y][x + i] = 'X'
        elif (direct == "south"):
            map[y - i][x] = 'X'
        else: # direct == "west"
            map[y][x - i] = 'X'

def test_ship_placement(ship,x,y,direct,map):
    # Returns true if ship can be placed with given settings.
    # Otherwise, returns false.
    global map_size, ship_size
    valid = True
    i = 0
    if ((x < 0) or (y < 0) or (x >= map_size) or (y >= map_size)):
        valid = False
    else:
        if (direct == "north"):
            if ((y + ship_size[ship]) >= map_size):
                valid = False
            else:
                while (i < ship_size[ship]) and valid:
                    if (map[y + i][x] != 'X'):
                        i = i + 1
                    else:
                        valid = False
        elif (direct == "south"):
            if ((y - ship_size[ship]) < 0):
                valid = False
            else:
                while (i < ship_size[ship]) and valid:
                    if (map[y - i][x] != 'X'):
                        i = i + 1
                    else:
                        valid = False
        elif (direct == "east"):
            if ((x + ship_size[ship]) >= map_size):
                valid = False
            else:
                while (i < ship_size[ship]) and valid:
                    if (map[y][x + i] != 'X'):
                        i = i + 1
                    else:
                        valid = False
        else: # direct == "west"
            if ((x - ship_size[ship]) < 0):
                valid = False
            else:
                while (i < ship_size[ship]) and valid:
                    if (map[y][x - i] != 'X'):
                        i = i + 1
                    else:
                        valid = False
    return valid

def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west
    """ Randomize all the ships position.
          ALTERNATIVE (see commented section) :
          For the second, third, and fourth ship, select between 1 or 2 spaces (1 - 3 for bigger map (14x14)) that go between currently
          selected ship and the previous ship.
          For each ship, the direction is perpendicular to the previously placed ship. """
    global map_size
    dummy_map = []
    for i in range(map_size):
        dummy_map.append([])
        for j in range(map_size):
            dummy_map[i].append('~')
    ships = ['Battleship','Carrier','Destroyer','Submarine']
    ship_command_placement = []

    # Placing the first ship
    ship_type = 'Cruiser'
    x = random.randint(0,map_size-1)
    y = random.randint(0,map_size-1)
    direct = random.choice(['north','south','east','west'])
    if (not test_ship_placement(ship_type,x,y,direct,dummy_map)):
        if (direct == "north"):
            direct = "south"
        elif (direct == "south"):
            direct = "north"
        elif (direct == "east"):
            direct = "west"
        else: # direct == "west"
            direct = "east"
    temp = ship_type + " " + str(x) + " " + str(y) + " " + direct
    print(temp)
    # Puts that information into the command queue
    ship_command_placement.append(temp)
    # Puts that information into the dummy map
    InsertShipIntoMap(temp,dummy_map)
    # Removes that ship type from the list of ships
    # ships.remove(ship_type)

    # Placing the 2nd - 4th ship
    """if (map_size >= 14):
        max_dist = 3
    else:
        max_dist = 2 """

    for i in range(3):
        # previous_ship = (copy.copy(ship_command_placement[-1])).split(" ")
        ship_type = random.choice(ships) # Randomize what ship will be put now
        valid = False
        while not valid:
            # The alternative way
            """ dist = random.choice([random.randint(1,max_dist),random.randint(0-max_dist,-1)])
            x = dist + int(previous_ship[1])
            y = dist + int(previous_ship[2])
            if ((previous_ship[3] == "north") or (previous_ship[3] == "south")):
                direct = random.choice(["east","west"])
            else:
                direct = random.choice(["north","south"])  """
            # Currently used steps - just randomize it
            x = random.randint(0,map_size-1)
            y = random.randint(0,map_size-1)
            direct = random.choice(['north','south','east','west'])
            valid = test_ship_placement(ship_type,x,y,direct,dummy_map)
        temp = ship_type + " " + str(x) + " " + str(y) + " " + direct
        print(temp)
        ship_command_placement.append(temp)
        # Removes that ship type from the list of ships
        ships.remove(ship_type)
        InsertShipIntoMap(temp,dummy_map)

    # Placing the last ship
    valid = False
    ship_type = ships[-1]
    while not valid:
        x = random.randint(0,map_size-1)
        y = random.randint(0,map_size-1)
        direct = random.choice(['north','south','east','west'])
        valid = test_ship_placement(ship_type,x,y,direct,dummy_map)

    temp = ship_type + " " + str(x) + " " + str(y) + " " + direct
    print(temp)
    ship_command_placement.append(temp)
    InsertShipIntoMap(temp,dummy_map)

    str_map = ""
    for line in dummy_map:
        for cell in line:
            str_map = str_map + cell
        str_map = str_map + "\n"
    print(str_map)
    # Outputting the results into the file to be read by the game
    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ship_command_placement:
            f_out.write(ship)
            f_out.write('\n')
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PlayerKey', nargs='?', help='Player key registered in the game')
    parser.add_argument('WorkingDirectory', nargs='?', default=os.getcwd(), help='Directory for the current game files')
    args = parser.parse_args()
    assert (os.path.isdir(args.WorkingDirectory))
    output_path = args.WorkingDirectory
    main(args.PlayerKey)
