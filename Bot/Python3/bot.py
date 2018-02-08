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
        * Random di area tengah map dengan metode papan catur
        * Jika kena :
            * Jika punya shot yang special, tembak special shot
                * Untuk setiap arah yang hit, lanjutkan ke arah tersebut dengan normal shot sampai kapal hancur
                * Jika shot tidak mengenai apapun, target dengan normal shot untuk arah yang belum dicoba, lalu ikuti aturan normal shot dibawah
            * Jika tidak ada shot special (lebih sering terjadi)
                * Coba kiri, kanan, atas, atau bawah (randomized). Jika tidak kena, coba untuk yang lainnya
                * Jika kena, teruskan ke arah tersebut sampai kapal hancur
    """

    targets = []
    for cell in opponent_map:
        if not cell['Damaged'] and not cell['Missed']:
            valid_cell = cell['X'], cell['Y']
            targets.append(valid_cell)
    target = random.choice(targets)
    output_shot(*target)
    return

def test_ship_placement(ship,x,y,direct,placed_ships):
    # Returns true if ship can be placed with given settings.
    # Otherwise, returns false.
    global map_size, ship_size
    if (direct == "north"):
        if ((y + ship_size[ship]) >= map_size):
            return false
        else:
            for i in range(len(placed_ships)):
                other_ship = placed_ships[i].split(" ")
    elif (direct == "south"):

    elif (direct == "east"):

    else: # direct == "west"


def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west
    """ Rules of placing the ship :
        * Randomize the placement of the first ship.
        * For the second, third, and fourth ship, select between 1 or 2 spaces (1 - 3 for bigger map (14x14)) that go between currently selected
          ship and the previous ship.
        * Randomize the last (fifth) ship.
        For each ship, the direction is perpendicular to the previously selected ship.
    """
    global map_size
    ships = ['Battleship','Carrier','Cruiser','Destroyer','Submarine']
    ship_command_placement = []

    # Placing the first ship
    ship_type = random.choice(ships)
    x = random.randint(0,map_size + 1)
    y = random.randint(0,map_size + 1)
    direct = random.choice(['north','south','east','west'])
    if (not test_ship_placement(ship_type,x,y,direct,ship_command_placement)):
        if (direct == "north"):
            direct = "south"
        elif (direct == "south"):
            direct = "north"
        elif (direct == "east"):
            direct = "west"
        else: # direct == "west"
            direct = "east"
    temp = ship_type + " " + str(x) + " " + str(y) + " " + direct
    ship_command_placement.append(temp)
    # Removes that ship type from the list of ships
    ships.remove(ship_type)

    # Placing the 2nd - 4th ship
    if (map_size >= 14):
        max_dist = 3
    else:
        max_dist = 2

    for i in range(3):
        previous_ship = copy.copy(ship_command_placement[:1]).split(" ")
        ship_type = random.choice(ships)
        xnow = random.choice([randint(1,max_dist),randint(0-max_dist,-1)])
        ynow = random.choice([randint(1,max_dist),randint(0-max_dist,-1)])
        if ((previous_ship[3] == "north") && (previous_ship[3] == "south"):

        else:

        

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
