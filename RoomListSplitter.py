'''
Created on Mar 9, 2017

@author: andrewbloomberg
'''


if __name__ == '__main__':
    file = open('roomlist.txt', 'r')
    roomlist = file.readlines()
    roomlist_tuples  = []
    for room in roomlist:
        room_number = room.split(" ")[0]
        building_name = room.split(" ", 1)[1].strip()
        roomlist_tuples.append((building_name, room_number, 123))
    print roomlist_tuples
    