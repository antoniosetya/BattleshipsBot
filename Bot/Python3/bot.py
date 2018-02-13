import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
output_path = '.'
map_size = 0
attack_status = "attackstatus.txt"

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


def output_shot2(x, y):
    move = 7
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
    targethit = state["PlayerMap"]["Owner"] ["ShotsHit"]
    prev_output_path = output_path[0:output_path.index(roundchar) + len(roundchar)]
    if playerkey == "B":
        prev_output_path = prev_output_path + " " + str(prevround) + "/B"
    else:
        prev_output_path = prev_output_path + " " + str(prevround) + "/A"

    if state["Round"] == 1:
        attackstatus = 0
        firsthitx = -1
        firsthity = -1
        x=-1
        y=-1
        attackdirection = 0
    else:
        #with open(os.path.join(prev_output_path, game_state_file), 'r') as f_inx:
        #   prevstate = json.load(f_inx)
        with open(os.path.join(prev_output_path, attack_status), 'r') as f_inz:
            prevstatus = f_inz.read().splitlines()
        prevattack = prevstatus[0]
        x,y = prevattack.split()
        currentship = ship_count(state['OpponentMap']['Ships'])
        attackstatus = 1000
        for cell in opponent_map1:
            if cell['Damaged'] and int(cell['X']) == int(x) and int(cell['Y']) == int(y):
                if int(prevstatus[4]) == -1 and int(prevstatus[5]) == -1:
                    attackstatus = 1
                    firsthitx = int(x)
                    firsthity = int(y)
                    attackdirection = 0
                elif int(prevstatus[2]) == int(currentship[0]) and int(currentship[1]) == 17-int(targethit):
                    attackstatus = 1
                    firsthitx = int(prevstatus[4])
                    firsthity = int(prevstatus[5])
                    if firsthitx < int(x):
                        attackdirection = 1 #right
                    elif firsthitx > int(x):
                        attackdirection = 2 #left
                    elif firsthity < int(y):
                        attackdirection = 3 #up
                    elif firsthity > int(y):
                        attackdirection = 4 #down
                elif int(prevstatus[2]) == int(currentship[0]) and int(currentship[1]) != 17-int(targethit):
                    attackstatus = 1
                    firsthitx = int(prevstatus[4])
                    firsthity = int(prevstatus[5])
                    if firsthitx < int(x):
                        attackdirection = 1
                    elif firsthitx > int(x):
                        attackdirection = 2
                    elif firsthity < int(y):
                        attackdirection = 3
                    elif firsthity > int(y):
                        attackdirection = 4
                elif int(prevstatus[2]) != int(currentship[0]) and int(currentship[1]) == 17-int(targethit):
                    attackstatus = 0
                    firsthitx = -1
                    firsthity = -1
                    attackdirection = 0
                elif int(prevstatus[2]) != int(currentship[0]) and int(currentship[1]) != 17-int(targethit):
                    attackstatus = 2
                    firsthitx = int(prevstatus[4])
                    firsthity = int(prevstatus[5])
                    attackdirection = 0
            elif cell['Missed'] and int(cell['X']) == int(x) and int(cell['Y']) == int(y):
                if int(prevstatus[4]) == -1 and int(prevstatus[5]) == -1:
                    attackstatus = 0
                    firsthitx = -1
                    firsthity = -1
                    attackdirection = 0
                elif int(prevstatus[4]) != -1 and int(prevstatus[5]) != -1:
                    attackstatus = 1
                    firsthitx = int(prevstatus[4])
                    firsthity = int(prevstatus[5])
                    attackdirection = 0
            elif int(cell['X']) == int(x) and int(cell['Y']) == int(y):
                attackstatus = 99999
                firsthitx = -9999
                firsthity = -9999
                attackdirection = -9999
    return attackstatus, firsthitx, firsthity, attackdirection,x,y

def fire_shot(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)

    #proses pengaksesan state sebelumnya
    
    attackstatus = attack_state(opponent_map)
    targets = []
    
    for cell in opponent_map:
        if not cell['Damaged'] and not cell['Missed'] and (int(cell['X']) + int(cell['Y'])) % 2 == 0 and int(attackstatus[0]) == 0:
            valid_cell = cell['X'], cell['Y']
            targets.append(valid_cell)
        elif int(attackstatus[3]) == 0:
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[1])+1 and int(cell['Y']) == int(attackstatus[2]):
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[1])-1 and int(cell['Y']) == int(attackstatus[2]):
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[1]) and int(cell['Y']) == int(attackstatus[2])-1:
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[1]) and int(cell['Y']) == int(attackstatus[2])+1:
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
        elif int(attackstatus[3]) == 1:
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[4])+1 and int(cell['Y']) == int(attackstatus[5]):
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
        elif int(attackstatus[3]) == 2:
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[4])-1 and int(cell['Y']) == int(attackstatus[5]):
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
        elif int(attackstatus[3]) == 3:
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[4]) and int(cell['Y']) == int(attackstatus[5])+1:
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
        elif int(attackstatus[3]) == 4:
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[4]) and int(cell['Y']) == int(attackstatus[5])-1:
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
        elif int(attackstatus[0]) == 2:
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) >= int(attackstatus[4])-3 and int(cell['X']) <= int(attackstatus[4])+3 and int(cell['Y']) <= int(attackstatus[5])+3 and int(cell['Y']) >= int(attackstatus[5])-3:
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
            
    if not targets:
        for cell in opponent_map:
            if not cell['Damaged'] and not cell['Missed'] and (int(cell['X']) + int(cell['Y'])) % 2 == 0 and int(attackstatus[0]) == 0:
                valid_cell = cell['X'], cell['Y']
                targets.append(valid_cell)
            if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1:
                if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[1])+1 and int(cell['Y']) == int(attackstatus[2]):
                    valid_cell = cell['X'], cell['Y']
                    targets.append(valid_cell)
                if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[1])-1 and int(cell['Y']) == int(attackstatus[2]):
                    valid_cell = cell['X'], cell['Y']
                    targets.append(valid_cell)
                if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[1]) and int(cell['Y']) == int(attackstatus[2])-1:
                    valid_cell = cell['X'], cell['Y']
                    targets.append(valid_cell)
                if not cell['Damaged'] and not cell['Missed'] and int(attackstatus[0]) == 1 and int(cell['X']) == int(attackstatus[1]) and int(cell['Y']) == int(attackstatus[2])+1:
                    valid_cell = cell['X'], cell['Y']
                    targets.append(valid_cell)

    target = choice(targets)
    with open(os.path.join(output_path, game_state_file), 'r') as f_inxx:
        state = json.load(f_inxx)
    if map_size == 10:
        energyround = 3
    elif map_size ==14:
        energyround = 4
    else:
        energyround = 2
    seekerenergy = energyround * 10
    """
    if int(attackstatus[0]) == 1 and state['PlayerMap']['Owner']['Energy'] >= seekerenergy  and int(attackstatus[3]) != 0:
        output_shot2(*target)
    else:
    """
    output_shot(*target)
    targetx = target[0]
    targety = target[1]
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
        f_out.write('\n')
        f_out.write('{}'.format(attackstatus[3]))
    return


def ship_count(enemy_location):
    count = 0
    sisa = 0
    for ship in enemy_location :
        if not ship['Destroyed']:
            count += 1
        if not ship['Destroyed'] and ship['ShipType'] == 'Submarine':
            sisa += 3
        if not ship['Destroyed'] and ship['ShipType'] == 'Battleship':
            sisa += 4
        if not ship['Destroyed'] and ship['ShipType'] == 'Carrier':
            sisa += 5
        if not ship['Destroyed'] and ship['ShipType'] == 'Cruiser':
            sisa += 3
        if not ship['Destroyed'] and ship['ShipType'] == 'Destroyer':
            sisa += 2
    return count,sisa

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
    ship_command_placement.append(temp)
    InsertShipIntoMap(temp,dummy_map)

    # Outputting the results into the file to be read by the game
    with open(os.path.join(output_path, place_ship_file), 'w') as f_out:
        for ship in ships:
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
