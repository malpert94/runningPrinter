import numpy as np
import time


def phrase_array(phr):  # convert text to an array of decimals from characters dictionary
    array = []
    for letter in range(len(phr)):
        for column in range(len(characters9[phr[letter]])):
            array.append(characters9[phr[letter]][column])
    return array


def adj_for_len(text, distance):  # adjusts length of array for distance of line and adjusts dot spacing for accuracy
    dotDist = 10 #14.816715493  # base for calculating distance between dots: CHANGE AS NECESSARY
    if distance == 0:  # if no line is required and distance is not specified
        newDotDist = dotDist  # dot spacing not changed
        array = text  # array size not changed
    elif distance < len(text)*dotDist:
        n = distance/dotDist
        newDotDist = distance/int(round(n))
        finalN = round(n)+1 - len(text)
        array = text[0:finalN]
    else:
        n = distance/dotDist
        newDotDist = distance/int(round(n))
        finalN = round(n)+1 - len(text)
        array = text
        array.extend([0 for i in range(finalN)])
    return array, newDotDist


def line_mask(text, lin):
    array = []
    for letter in range(len(text)):
        tobin = '{0:09b}'.format(text[letter] | lines[lin])  # Change to '{0:07b}' for seven
        array.append(tobin)
    return array


'''
def phrase_array(phr, lin, distance):  # convert text to an array of
    array = []
    f = distance  # This is where the calculations for distance must happen
    for letter in range(len(phr)):  # loop for each letter
        for column in range(len(characters[phr[letter]])):
            tobin = '{0:07b}'.format(characters[phr[letter]][column] | lines[lin])
            array.append(tobin)  # add column to phrase array
    return array
'''

def lsb_top(array, nozzle_count, matrix):
    for job in range(len(array)):  # make matrix with lsb in row 0
        for bit in range(nozzle_count):
            matrix[(nozzle_count-1)-bit, job] = str(array[job][bit])
    return matrix


def msb_top(array, nozzle_count, matrix):
    for job in range(len(array)):  # make matrix with msb in row 0
        for bit in range(nozzle_count):
            matrix[bit, job] = str(array[job][bit])
    return matrix


def top_shift(matrix, nozzle_count):
    for shift in range((nozzle_count-1)):  # shift rows from top first
        matrix[shift] = np.roll(matrix[shift], (nozzle_count-1)-shift)
    return matrix


def bottom_shift(matrix, nozzle_count):
    for shift in range(nozzle_count):  # shift rows from top first
        matrix[shift] = np.roll(matrix[shift], shift)  # (nozzles-1)-shift)
    return matrix


def to_print(matrix):
    matrix2 = np.transpose(matrix)
    for vector in range(len(matrix[0])):
        matrix2[vector] = np.flip(matrix2[vector], 0)
    powers = np.array([2**(nozzles-1-i) for i in range(nozzles)])
    matrix3 = []
    for row in range(len(matrix2)):
        matrix3.append(np.dot(matrix2[row],powers))
    return matrix3


def create_array(phrase, line, direction, dist):
    array = phrase_array(phrase)  #, line, dist)
    [array2, space] = adj_for_len(array, dist)
    array3 = line_mask(array2, line)
    matrix = np.zeros((nozzles, len(array3)+(nozzles-1)), dtype=int)
    if direction == 'n' or direction == 'N':
        lsb_top(array3, nozzles, matrix)
        matrix = top_shift(matrix, nozzles)
    elif direction == 's' or direction == 'S':
        msb_top(array3, nozzles, matrix)
        matrix = top_shift(matrix, nozzles)
    elif direction == 'e' or direction == 'E':
        msb_top(array3, nozzles, matrix)
        matrix = bottom_shift(matrix, nozzles)
    elif direction == 'w' or direction == 'W':
        lsb_top(array3, nozzles, matrix)
        matrix = bottom_shift(matrix, nozzles)
    printJob = to_print(matrix)
    return printJob, space


characters = {' ': [0, 0, 0, 0],
              '!': [46, 0],
              '"': [6, 0, 6, 0],
              '#': [20, 62, 20, 62, 20, 0],
              '$': [36, 42, 62, 42, 18, 0],
              '%': [34, 16, 8, 4, 34, 0],
              '&': [20, 42, 42, 60, 40, 0],
              "'": [6, 0],
              '(': [28, 34, 0],
              ')': [34, 28, 0],
              '*': [18, 12, 30, 12, 18, 0],
              '+': [8, 28, 8, 0],
              ',': [32, 16, 0],
              '-': [8, 8, 8, 0],
              '.': [32, 0, 0, 0, 0],
              '/': [32, 16, 8, 4, 2, 0],
              '0': [28, 50, 42, 38, 28, 0],
              '1': [36, 62, 32, 0],
              '2': [50, 42, 42, 42, 36, 0],
              '3': [34, 34, 42, 42, 20, 0],
              '4': [6, 8, 8, 8, 62, 0],
              '5': [46, 42, 42, 42, 18, 0],
              '6': [28, 42, 42, 42, 18, 0],
              '7': [2, 2, 2, 58, 6, 0],
              '8': [20, 42, 42, 42, 20, 0],
              '9': [4, 42, 42, 42, 28, 0],
              ':': [20, 0],
              ';': [32, 20, 0],
              '<': [8, 20, 34, 0],
              '=': [20, 20, 20, 0],
              '>': [34, 20, 8, 0],
              '?': [4, 2, 42, 10, 4, 0],
              '@': [28, 34, 10, 18, 28, 0],
              'A': [60, 10, 10, 10, 60, 0],
              'B': [62, 42, 42, 42, 20, 0],
              'C': [28, 34, 34, 34, 34, 0],
              'D': [62, 34, 34, 34, 28, 0],
              'E': [62, 42, 42, 42, 42, 0],
              'F': [62, 10, 10, 2, 2, 0],
              'G': [28, 34, 42, 42, 58, 0],
              'H': [62, 8, 8, 8, 62, 0],
              'I': [34, 62, 34, 0],
              'J': [16, 32, 34, 34, 30, 0],
              'K': [62, 8, 12, 10, 48, 0],
              'L': [62, 32, 32, 32, 32, 0],
              'M': [62, 4, 8, 4, 62, 0],
              'N': [62, 2, 28, 32, 62, 0],
              'O': [28, 34, 34, 34, 28, 0],
              'P': [62, 10, 10, 10, 4, 0],
              'Q': [28, 34, 34, 60, 32, 0],
              'R': [62, 10, 10, 26, 36, 0],
              'S': [36, 42, 42, 42, 18, 0],
              'T': [2, 2, 62, 2, 2, 0],
              'U': [30, 32, 32, 32, 30, 0],
              'V': [6, 24, 32, 24, 6, 0],
              'W': [62, 16, 8, 16, 62, 0],
              'X': [34, 20, 8, 20, 34, 0],
              'Y': [6, 8, 56, 8, 6, 0],
              'Z': [50, 42, 42, 42, 38, 0],
              '[': [62, 34, 0],
              '\\': [2, 4, 8, 16, 32, 0],
              ']': [34, 62, 0],
              '^': [4, 2, 4, 0],
              '_': [32, 32, 32, 32],
              '`': [2, 4, 0],
              'a': [18, 42, 42, 42, 60, 0],
              'b': [62, 36, 36, 36, 24, 0],
              'c': [28, 34, 34, 34, 20, 0],
              'd': [24, 36, 36, 36, 62, 0],
              'e': [28, 42, 42, 42, 44, 0],
              'f': [60, 10, 10, 2, 2, 0],
              'g': [36, 42, 42, 42, 28, 0],
              'h': [62, 4, 4, 4, 56, 0],
              'i': [58, 0],
              'j': [32, 32, 32, 32, 30, 0],
              'k': [62, 8, 8, 20, 34, 0],
              'l': [34, 62, 32, 0],
              'm': [62, 2, 60, 2, 60, 0],
              'n': [62, 4, 2, 2, 60, 0],
              'o': [28, 34, 34, 34, 28, 0],
              'p': [62, 18, 18, 18, 12, 0],
              'q': [12, 18, 18, 18, 62, 0],
              'r': [62, 4, 2, 2, 4, 0],
              's': [36, 42, 42, 42, 18, 0],
              't': [30, 36, 36, 32, 16, 0],
              'u': [30, 32, 32, 16, 62, 0],
              'v': [6, 24, 32, 24, 6, 0],
              'w': [30, 32, 30, 32, 30, 0],
              'x': [54, 8, 8, 8, 54, 0],
              'y': [38, 40, 40, 40, 30, 0],
              'z': [34, 50, 42, 38, 34, 0],
              '{': [8, 28, 34, 0],
              '|': [62, 0],
              '}': [34, 28, 8, 0],
              '~': [8, 4, 8, 4, 0]}


characters9 = {' ': [0, 0, 0, 0, 0],
               '!': [190, 0],
               '"': [6, 0, 6, 0],
               '#': [80, 248, 80, 248, 80, 0],
               '$': [92, 84, 254, 84, 116, 0],
               '%': [70, 38, 16, 200, 196, 0],
               '&': [108, 146, 146, 108, 144, 0],
               "'": [6, 0],
               '(': [56, 68, 130, 0],
               ')': [130, 68, 56, 0],
               '*': [8, 42, 28, 28, 42, 8, 0],
               '+': [16, 16, 124, 16, 16, 0],
               ',': [128, 64, 0],
               '-': [16, 16, 16, 16, 16, 0],
               '.': [128, 0],
               '/': [128, 64, 32, 16, 8, 4, 2, 0],
               '0': [124, 162, 146, 138, 124, 0],
               '1': [132, 254, 128, 0],
               '2': [140, 194, 162, 146, 140, 0],
               '3': [68, 130, 146, 146, 108, 0],
               '4': [48, 40, 36, 254, 32, 0],
               '5': [158, 146, 146, 146, 98, 0],
               '6': [124, 146, 146, 146, 96, 0],
               '7': [2, 2, 194, 50, 14, 0],
               '8': [108, 146, 146, 146, 108, 0],
               '9': [12, 146, 146, 146, 124, 0],
               ':': [72, 0],
               ';': [128, 72, 0],
               '<': [16, 40, 68, 0],
               '=': [40, 40, 40, 40, 40, 0],
               '>': [68, 40, 16, 0],
               '?': [12, 2, 178, 18, 12, 0],
               '@': [56, 68, 146, 170, 178, 36, 56, 0],
               'A': [252, 18, 18, 18, 252, 0],
               'B': [254, 146, 146, 146, 108, 0],
               'C': [124, 130, 130, 130, 68, 0],
               'D': [254, 130, 130, 130, 124, 0],
               'E': [254, 146, 146, 146, 130, 0],
               'F': [254, 18, 18, 18, 2, 0],
               'G': [124, 130, 146, 146, 116, 0],
               'H': [254, 16, 16, 16, 254, 0],
               'I': [130, 254, 130, 0],
               'J': [64, 128, 130, 130, 126, 0],
               'K': [254, 16, 40, 68, 130, 0],
               'L': [254, 128, 128, 128, 128, 0],
               'M': [254, 4, 8, 4, 254, 0],
               'N': [254, 8, 16, 32, 254, 0],
               'O': [124, 130, 130, 130, 124, 0],
               'P': [254, 18, 18, 18, 12, 0],
               'Q': [124, 130, 162, 66, 188, 0],
               'R': [254, 18, 18, 18, 236, 0],
               'S': [76, 146, 146, 146, 100, 0],
               'T': [2, 2, 254, 2, 2, 0],
               'U': [126, 128, 128, 128, 126, 0],
               'V': [14, 48, 192, 48, 14, 0],
               'W': [254, 64, 48, 64, 254, 0],
               'X': [198, 40, 16, 40, 198, 0],
               'Y': [6, 8, 240, 8, 6, 0],
               'Z': [194, 162, 146, 138, 134, 0],
               '[': [254, 130, 0],
               '\\': [2, 4, 8, 16, 32, 64, 128, 0],
               ']': [130, 254, 0],
               '^': [8, 4, 2, 4, 8, 0],
               '_': [128, 128, 128, 128, 128, 0],
               '`': [2, 4, 0],
               'a': [64, 168, 168, 240, 0],
               'b': [252, 144, 144, 96, 0],
               'c': [112, 136, 136, 80, 0],
               'd': [96, 144, 144, 252, 0],
               'e': [112, 168, 168, 176, 0],
               'f': [8, 252, 10, 10, 0],
               'g': [152, 164, 164, 124, 0],
               'h': [254, 16, 16, 224, 0],
               'i': [244, 0],
               'j': [64, 128, 128, 122, 0],
               'k': [254, 32, 80, 136, 0],
               'l': [126, 128, 128, 0],
               'm': [248, 8, 248, 8, 240, 0],
               'n': [248, 8, 8, 8, 240, 0],
               'o': [112, 136, 136, 136, 112, 0],
               'p': [248, 72, 72, 48, 0],
               'q': [48, 72, 72, 248, 0],
               'r': [240, 8, 8, 16, 0],
               's': [144, 168, 168, 72, 0],
               't': [8, 124, 136, 128, 0],
               'u': [120, 128, 128, 248, 0],
               'v': [24, 96, 128, 96, 24, 0],
               'w': [120, 128, 96, 128, 120, 0],
               'x': [136, 80, 32, 80, 136, 0],
               'y': [152, 160, 160, 120, 0],
               'z': [200, 168, 152, 136, 0],
               '{': [16, 108, 130, 0],
               '|': [254, 0],
               '}': [130, 108, 16, 0],
               '~': [16, 8, 16, 8, 0],
               '£': [144, 252, 146, 146, 132, 0]}

# lines = np.array([0, 1, 8, 64, 65])
lines = np.array([0, 256, 16, 1, 257])


nozzles = 9
