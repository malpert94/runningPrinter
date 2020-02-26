import numpy as np
import time

def phrase_array(phr, lin, distance):  # convert text to an array of
    array = []
    f = distance  # This is where the calculations for distance must happen
    for letter in range(len(phr)):  # loop for each letter
        for column in range(len(characters[phr[letter]])):
            tobin = '{0:07b}'.format(characters[phr[letter]][column] | lines[lin])
            array.append(tobin)  # add column to phrase array
    return array


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


def create_array(phrase, line, direction, distance):
    array = phrase_array(phrase, line, distance)
    matrix = np.zeros((nozzles, len(array)+(nozzles-1)), dtype=int)
    if direction == 'n' or direction == 'N':
        lsb_top(array, nozzles, matrix)
        matrix = top_shift(matrix, nozzles)
    elif direction == 's' or direction == 'S':
        msb_top(array, nozzles, matrix)
        matrix = top_shift(matrix, nozzles)
    elif direction == 'e' or direction == 'E':
        msb_top(array, nozzles, matrix)
        matrix = bottom_shift(matrix, nozzles)
    elif direction == 'w' or direction == 'W':
        lsb_top(array, nozzles, matrix)
        matrix = bottom_shift(matrix, nozzles)
    printJob = to_print(matrix)
    return printJob


characters = {'A': [60, 10, 10, 10, 60, 0],
              'B': [62, 42, 42, 42, 20, 0],
              'C': [28, 34, 34, 34, 34, 0],
              'D': [62, 34, 34, 34, 28, 0],
              'E': [62, 42, 42, 42, 42, 0],
              'F': [62, 10, 10, 2, 2, 0],
              'G': [28, 34, 42, 42, 58, 0],
              'H': [62, 8, 8, 8, 62, 0],
              'I': [34, 62, 34, 0, 0, 0],
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
              '0': [20, 50, 42, 38, 20, 0],
              '1': [36, 62, 32, 0, 0, 0],
              '2': [50, 42, 42, 42, 36, 0],
              '3': [34, 34, 42, 42, 20, 0],
              '4': [6, 8, 8, 8, 62, 0],
              '5': [46, 42, 42, 42, 18, 0],
              '6': [28, 42, 42, 42, 18, 0],
              '7': [2, 2, 2, 58, 6, 0],
              '8': [20, 42, 42, 42, 20, 0],
              '9': [4, 10, 42, 42, 20, 0],
              ' ': [0, 0, 0, 0],
              '.': [32, 0, 0, 0, 0]}


lines = np.array([0, 1, 8, 64, 65])
nozzles = 7
'''
phrase = "Rugged Robotics Blueprint UT Tyler"  # input('Phrase to print: ')
line = 4  # int(input('Line to print: '))
direction = "n"  # input('Direction: ')
distance = 30  # 14.8167mm

hey = create_array(phrase, line, direction, distance)
print(hey)

'''