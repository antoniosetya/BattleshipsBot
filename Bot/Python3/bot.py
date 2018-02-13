import argparse
import json
import os
from random import choice

command_file = "command.txt"
place_ship_file = "place.txt"
game_state_file = "state.json"
round_command_file = "roundCommand.json"
output_path = '.'
map_size = 0
attack_status_file = "attackStatus.json"

ship_size = {"Submarine" : 3,
            "Battleship" : 4,
            "Carrier" : 5,
            "Cruiser" : 3,
            "Destroyer" : 2}

last_shot_file = "lastShot.json"

""" DEFINE THE AttackStatus:
    
"""

def main(player_key):
    global map_size

    # Retrieve current game state
    with open(os.path.join(output_path, game_state_file), 'r') as f_in:
        state = json.load(f_in)

    map_size = state['MapDimension']

    setSomeConstant(map_size)

    if state['Phase'] == 1:
        place_ships()
        state['Phase'] = 2
    elif state['Phase'] == 2:
        next_phase = fire_shot_inner(state['OpponentMap']['Cells'])
        state['Phase'] = next_phase
    else:
        fire_shot_outer(state['OpponentMap']['Cells'])


#set some constant that will be used in this program
def setSomeConstant(map_size):
    global center
    center = map_size/2
    global radius
    if map_size==7:
        radius = 1
    elif map_size==10:
        radius = 2
    else:
        radius = 3
    global lowerX
    lowerX = center-radius
    global higherX
    higherX = center + radius
    global lowerY
    lowerY = center - radius
    global higherY
    higherY = center + radius


def output_shot(x, y):
    move = 1  # 1=fire shot command code
    with open(os.path.join(output_path, command_file), 'w') as f_out:
        f_out.write('{},{},{}'.format(move, x, y))
        f_out.write('\n')
    pass
    


def fire_shot_outer(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)

    targets = []
    for cell in opponent_map:
        X_position = int(cell['X'])
        if not cell['Damaged'] and not cell['Missed']:
            #a = int(cell['X'])
            valid_cell = cell['X'], cell['Y']
            targets.append(valid_cell)
            with open("debugging.txt","a") as file_object:
                file_object.write(str(valid_cell))
                file_object.write("\n")
                
    target = choice(targets)
    output_shot(*target)

    save_last_shot(target[0], target[1],isSuccess)



    with open(os.path.join(output_path, attack_status_file), 'w') as f_out:
        lastStatus = {}
        lastStatus['TargetX'] = targetX
        lastStatus['TargetY'] = targetY
        lastStatus['CountBoat'] = countBoat
        lastStatus['AttackStatus'] = attackStatus
        lastStatus['FirstHitX'] = firstHitX
        lastStatus['FirstHitY'] = firstHitY
        json.dump(lastStatus, f_out)
    return

#returns how many ship and the tiles that needed to be destroy
def ship_count(enemy_location):
    count = 0
    sisa = 0
    max_size = 0
    for ship in enemy_location :
        if not ship['Destroyed']:
            count += 1
        if ship['ShipType'] == 'Submarine' :
            sisa += 3
            if max_size < 3:
                max_size = 3
        if ship['ShipType'] == 'Battleship' :
            sisa += 4
            if max_size < 4:
                max_size = 4
        if ship['ShipType'] == 'Carrier' :
            sisa += 5
            if max_size < 5:
                max_size = 5
        if ship['ShipType'] == 'Cruiser' :
            sisa += 3
            if max_size < 3:
                max_size = 3
        if ship['ShipType'] == 'Destroyer':
            sisa += 2
            if max_size < 2:
                max_size = 2
    return count, sisa, max_size


def save_last_status(dictionary):
    with open(os.path.join(output_path, attack_status_file), 'w') as f_out:
        lastStatus = {}
        lastStatus['TargetX'] = dictionary['TargetX']
        lastStatus['TargetY'] = dictionary['TargetY']
        lastStatus['AttackStatus'] = dictionary['AttackStatus']
        lastStatus['FirstHitX'] = dictionary['FirstHitX']
        lastStatus['FirstHitY'] = dictionary['FirstHitY']
        lastStatus['ShipMaxSize'] = dictionary['ShipMaxSize']
        lastStatus['ShipTiles'] = dictionary['ShipTiles']
        lastStatus['ShipAvailable'] = dictionary['ShipAvailable'] #number of enemy ships available
        lastStatus['Direction'] = dictionary['Direction']
        json.dump(lastStatus, f_out)


#returns the last attack attempted
def read_last_status():
    prevround = state["Round"] - 1
    roundchar = "Round"
    playerkey = state["PlayerMap"]["Owner"]["Key"]
    prev_output_path = output_path[0:output_path.index(roundchar) + len(roundchar)]
    if playerkey == "B":
        prev_output_path = prev_output_path + " " + str(prevround) + "/B"
    else:
        prev_output_path = prev_output_path + " " + str(prevround) + "/A"
    with open(os.path.join(prev_output_path, attack_status_file), 'r') as last_attack_status:
        return json.load(last_attack_status)

def read_prev_prev_status():
    prevround = state["Round"] - 2
    roundchar = "Round"
    playerkey = state["PlayerMap"]["Owner"]["Key"]
    prev_output_path = output_path[0:output_path.index(roundchar) + len(roundchar)]
    if playerkey == "B":
        prev_output_path = prev_output_path + " " + str(prevround) + "/B"
    else:
        prev_output_path = prev_output_path + " " + str(prevround) + "/A"
    with open(os.path.join(prev_output_path, attack_status_file), 'r') as last_attack_status:
        return json.load(last_attack_status)

def attack_mode(opponent_map, enemy_location):
    attack_state = next_state_determiner(opponent_map)
    dictionary_save = {}
    dictionary_save['AttackStatus'] = attack_state
    dictionary_save['ShipAvailable'], dictionary_save['ShipTiles'], dictionary_save['ShipMaxSize'] = ship_count(enemy_location)

    #set the default
    dictionary_save['Direction'] = 'east'
    dictionary_save['FirstHitX'] = -1
    dictionary_save['FirstHitY'] = -1

    #direction used in attack mode 1 and 2
    west = prevStatus['TargetX'] - 1, prevStatus['TargetY']
    east = prevStatus['TargetX'] + 1, prevStatus['TargetY']
    north = prevStatus['TargetX'], prevStatus['TargetY'] + 1
    south = prevStatus['TargetX'], prevStatus['TargetY'] + 1


    if attack_state == 0:
        #SEARCH A TARGET
        for cell in opponent_map:
            if not cell['Damaged'] and not cell['Missed'] :
                #inner cell for the next improvement
                """and int(cell['X']) >= lowerX and int(cell['X']) <= higherXand int(cell['Y']) >= lowerY and int(cell['Y']) <= higherY and (int(cell['X']) + int(cell['Y'])) % 2 == 0:"""
                target = cell['X'], cell['Y']
                break
        output_shot(*target)

    elif attack_state == 1:

        for cell in opponent_map:
            #attack a tiles which is the west or east or north or south of the center
            if not cell['Damaged'] and not cell['Missed'] and ( (int(cell['X']), int(cell['Y'])) == west or (int(cell['X']), int(cell['Y'])) == east or (int(cell['X']), int(cell['Y'])) == north or (int(cell['X']), int(cell['Y'])) == south):
                target = cell['X'], cell['Y']
                output_shot(*target)
                dictionary_save['FirstHitX'] = int(cell['X'])
                dictionary_save['FirstHitY'] = int(cell['Y'])
                # SAVE THE DIRECTION
                if (int(cell['X']), int(cell['Y'])) == west:
                    dictionary_save['Direction'] = 'west'
                elif (int(cell['X']), int(cell['Y'])) == east:
                    dictionary_save['Direction'] = 'east'
                elif (int(cell['X']), int(cell['Y'])) == north:
                    dictionary_save['Direction'] = 'north'
                elif (int(cell['X']), int(cell['Y'])) == south):
                    dictionary_save['Direction'] = 'south'

                dictionary_save['TargetX'] = int(cell['X'])
                dictionary_save['TargetY'] = int(cell['Y'])

                break

    elif attack_state == 2:
        if prevStatus['Direction']=='west':
            target = west
        elif prevStatus['Direction']=='east':
            target = east
        elif prevStatus['Direction'] == 'north':
            target = north
        else: #south
            target = south

        output_shot(*target)
        #save the states

    dictionary_save['TargetX'] = target[0]
    dictionary_save['TargetY'] = target[1]
    save_last_status(dictionary_save)

def next_state_determiner(opponent_map):
    prevStatus = read_last_status()
    prevPrevStatus = read_prev_prev_status()
    LAST_ATTACK_SUCCESS = False
    for cell in opponent_map:
        # if the last attack hit
        if int(prevStatus['TargetX']) == int(cell['X']) and int(prevStatus['TargetY']) == int(cell['Y']) and cell[
            'Damaged']:
            LAST_ATTACK_SUCCESS = True
            if prevStatus['AttackStatus'] == 0:  # SEARCHING MODE
                # if doesn't succeed, searching again (mode 0)
                # if succeed, to attack mode 1
                # ATTACK MODE 1
                next_attack_mode = 1
            elif prevStatus['AttackStatus'] == 1:  # HAVE ATTACKED IN AT LEAST ONE DIRECTION
                # if succeed, to ATTACK MODE 3
                next_attack_mode = 2
                # if doesn't success, back to attack mode and attack another direction
            elif prevStatus['AttackStatus'] == 2:
                # if destroyed, back to mode 0 (searching)
                # IMPLEMENT TO CHECK DESTROYED SHIP
                # destroyed if the last status is less than it's previous
                if destroyed:
                    next_attack_mode = 0
                elif atEdge:
                    next_attack_mode = 2
                else:
                    next_attack_mode = 2
                    # if haven't destroyed hit, to mode 3
                    # if haven't destroyed and missed


    # if the last shot missed
    if not LAST_ATTACK_SUCCESS:
        if prevStatus['AttackStatus'] == 0:
            next_attack_mode = 0
        elif prevStatus['AttackStatus'] == 1:
            next_attack_mode = 1
        elif prevStatus['AttackStatus'] == 2:
            next_attack_mode = 1

    return next_attack_mode

def fire_shot_inner(opponent_map):
    # To send through a command please pass through the following <code>,<x>,<y>
    # Possible codes: 1 - Fireshot, 0 - Do Nothing (please pass through coordinates if
    #  code 1 is your choice)

    attack_state(opponent_map)



def place_ships():
    # Please place your ships in the following format <Shipname> <x> <y> <direction>
    # Ship names: Battleship, Cruiser, Carrier, Destroyer, Submarine
    # Directions: north east south west

    ships = ['Battleship 1 0 north',
             'Carrier 3 1 East',
             'Cruiser 4 2 north',
             'Destroyer 7 3 north',
             'Submarine 1 8 East'
             ]

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





def attack_state(opponent_map):
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
        firstHitX = -1
        firstHitY = -1
    else:
        with open(os.path.join(prev_output_path, game_state_file), 'r') as f_inx:
            prevstate = json.load(f_inx)
        with open(os.path.join(prev_output_path, attack_status_file), 'r') as f_inz:
            prevStatus = json.load(f_inz)
        currentship = ship_count(state['OpponentMap']['Ships'])
        for cell in opponent_map:
            if cell['Damaged'] and int(cell['X']) == int(x) and int(cell['Y']) == int(y):
                if int(prevStatus['X']) == -1 and int(prevStatus['Y']) == -1:
                    attackstatus = 1
                    firstHitX = int(x)
                    firstHitY = int(y)
                elif int(prevstatus[2]) != int(currentship[0]) and int(currentship[1]) != \
                        int(state['Owner']['Ships']['ShotsHit']):
                    attackstatus = 1
                    firsthitx = int(prevstatus[4])
                    firsthity = int(prevstatus[5])
                elif int(prevstatus[2]) != int(currentship[0]) and int(currentship[1]) == int(
                        state['Owner']['Ships']['ShotsHit']):
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

