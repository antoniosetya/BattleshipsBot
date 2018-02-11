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


def attack_state(opponent_map1):
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)

    prevround = state["Round"] - 1
    roundchar = "Round"
    playerkey = state["PlayerMap"]["Owner"]["Key"]
    prev_output_path = output_path[0:output_path.index(roundchar) + len(roundchar)]
    if playerkey == "B":
        prev_output_path = prev_output_path + " " + str(prevround) + "/B"
    else:
        prev_output_path = prev_output_path + " " + str(prevround) + "/A"

    if state["Round"] == 1:
        attackstatus = 0
        firsthitx = -1
        firsthity = -1
    else:
        with open(os.path.join(prev_output_path, game_state_file), 'r') as f_inx:
            prevstate = json.load(f_inx)
        with open(os.path.join(prev_output_path, attack_status), 'r') as f_inz:
            prevstatus = f_inz.read().splitlines()
        prevattack = prevstatus[0]
        x,y = prevattack.split()
        currentship = ship_count(state['OpponentMap']['Ships'])
        for cell in opponent_map1:
            if cell['Damaged'] and int(cell['X']) == int(x) and int(cell['Y']) == int(y):
                if int(prevstatus[4]) == -1 and int(prevstatus[5]) == -1:
                    attackstatus = 1
                    firsthitx = int(x)
                    firsthity = int(y)
                elif int(prevstatus[2]) != int(currentship[0]) and int(currentship[1]) != int(state['Owner']['Ships']['ShotsHit']):
                    attackstatus = 1
                    firsthitx = int(prevstatus[4])
                    firsthity = int(prevstatus[5])
                elif int(prevstatus[2]) != int(currentship[0]) and int(currentship[1]) == int(state['Owner']['Ships']['ShotsHit']):
                    attackstatus = 0
                    firsthitx = -1
                    firsthity = -1
            elif cell['Missed'] and int(cell['X']) == int(x) and int(cell['Y']) == int(y):
                if int(prevstatus[4]) == -1 and int(prevstatus[5]) == -1:
                    attackstatus = 0
                    firsthitx = -1
                    firsthity = -1
                elif int(prevstatus[4]) != -1 and int(prevstatus[5]) != -1:
                    attackstatus = 1
                    firsthitx = int(prevstatus[4])
                    firsthity = int(prevstatus[5])
            
    return attackstatus, firsthitx, firsthity

def fire_shot(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)

    #proses pengaksesan state sebelumnya
    
    attackstatus = attack_state(opponent_map)
    targets = []
    if map_size == 10 :
	    for cell in opponent_map:
	        if not cell['Damaged'] and not cell['Missed'] and (int(cell['X'])+ int(cell['Y']))%2 == 0:
	            valid_cell = cell['X'], cell['Y']
	            targets.append(valid_cell)
    target = choice(targets)
    output_shot(*target)
    targetx = target[0]
    targety = target[1]
    with open(os.path.join(output_path, game_state_file), 'r') as f_inxx:
        state = json.load(f_inxx)
    enemyboatcount = ship_count(state['OpponentMap']['Ships'])
    countboat = enemyboatcount[0]
    countsisa = enemyboatcount[1]
    
    
    
    with open(os.path.join(output_path, attack_status), 'w') as f_out:
        f_out.write('{} {}'.format(targetx,targety))
        f_out.write('\n')
        f_out.write('{}'.format(attackstatus[0]))
        f_out.write('\n')
        f_out.write('{}'.format(countboat))
        f_out.write('\n')
        f_out.write('{}'.format(countsisa))
        f_out.write('\n')
        f_out.write('{}'.format(attackstatus[1]))
        f_out.write('\n')
        f_out.write('{}'.format(attackstatus[2]))

    return


def ship_count(enemy_location):
    count = 0
    sisa = 0
    for ship in enemy_location :
        if not ship['Destroyed']:
            count += 1
        if ship['ShipType'] == 'Submarine' :
            sisa += 3
        if ship['ShipType'] == 'Battleship' :
            sisa += 4
        if ship['ShipType'] == 'Carrier' :
            sisa += 5
        if ship['ShipType'] == 'Cruiser' :
            sisa += 3
        if ship['ShipType'] == 'Destroyer':
            sisa += 2
    return count,sisa

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
    """ Rules of placing the ship :
        * Randomize the placement of the first ship.
        * For the second, third, and fourth ship, select between 1 or 2 spaces (1 - 3 for bigger map (14x14)) that go between currently
          selected ship and the previous ship.
          ALTERNATIVE : Just randomize it. On testing, this has proven to be better, quicker, and safer way. (code in comments in that section)
        * Randomize the last (fifth) ship.
        For each ship, the direction is perpendicular to the previously placed ship.
    """
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
    #ships.remove(ship_type)

    # Placing the 2nd - 4th ship
    if (map_size >= 14):
        max_dist = 3
    else:
        max_dist = 2

    for i in range(3):
        previous_ship = (copy.copy(ship_command_placement[-1])).split(" ")
        ship_type = random.choice(ships)
        valid = False
        while not valid:
            dist = random.choice([random.randint(1,max_dist),random.randint(0-max_dist,-1)])
            x = dist + int(previous_ship[1])
            y = dist + int(previous_ship[2])
            if ((previous_ship[3] == "north") or (previous_ship[3] == "south")):
                direct = random.choice(["east","west"])
            else:
                direct = random.choice(["north","south"])
            #x = random.randint(0,map_size-1)
            #y = random.randint(0,map_size-1)
            #direct = random.choice(['north','south','east','west'])

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
