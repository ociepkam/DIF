import numpy as np
import random
from copy import deepcopy
from psychopy import logging

from sources.parameters import ALPHABET, ALL_LINES

"""
line['type'] = row

line_number 0 [['GL', 'SC', 'LL'],
line_number 1  ['EO', 'PO', 'EL'],
line_number 2  ['TL', 'RP', 'OL']]

line['type'] = column

 ln 0,  ln 1, ln 2
[['GL', 'SC', 'LL'],
 ['EO', 'PO', 'EL'],
 ['TL', 'RP', 'OL']]

line['type'] = diagonal

ln 0                  ln 1
    [['GL', 'SC', 'LL'],
     ['EO', 'PO', 'EL'],
     ['TL', 'RP', 'OL']]

"""


class Matrix:
    def __init__(self, n=3, possible_answers=ALL_LINES + ['no']):
        assert n > 2, "n have to be grater than 2"
        self.n = n
        self.possible_answers = possible_answers
        self.answer_line_type = random.choice(possible_answers)

        self.matrix = np.empty([n, n], dtype="unicode")
        self.matrix.fill('')

        if self.answer_line_type in ['row', 'column']:
            self.answer_line_number = random.choice(list(range(n)))
        elif self.answer_line_type == 'diagonal':
            self.answer_line_number = random.choice([0, 1])
        elif self.answer_line_type == 'no':
            self.answer_line_number = -1
        else:
            logging.error(self.answer_line_type + " is wrong value in possible_answers")
            raise Exception(self.answer_line_type + " is wrong value in possible_answers")

    # --------------- Matrix generation ------------------ #
    def fill_line(self, line_elements, line_positions):
        for elem, pos in zip(line_elements, line_positions):
            self.matrix[pos[0], pos[1]] = elem

    def fill_matrix(self, distractors=False):
        # fill answer line
        if self.answer_line_type != "no":
            answer_line_positions = self.get_line_positions(self.answer_line_type, self.answer_line_number)
            answer_line_elements = np.random.choice(ALPHABET, self.n, replace=False)
            self.fill_line(answer_line_elements, answer_line_positions)

        # fill rest
        while True:
            line_to_fill = self.get_line_to_fill()
            if not line_to_fill:
                break

            old_letters = [str(elem) for elem in line_to_fill['values'] if elem != '']
            alphabet = [elem for elem in ALPHABET if elem not in old_letters]
            n_elements_to_fill = self.n - line_to_fill["filling"]
            new_letters = np.random.choice(alphabet, n_elements_to_fill - 1)
            letters = np.concatenate((new_letters, old_letters), axis=None)
            duplicate = np.random.choice(letters)
            new_letters = np.concatenate((new_letters, duplicate), axis=None)
            np.random.shuffle(new_letters)
            new_line_value = []
            i = 0
            for elem in line_to_fill['values']:
                if elem == '':
                    new_line_value.append(new_letters[i])
                    i += 1
                else:
                    new_line_value.append(elem)
            self.fill_line(new_line_value, line_to_fill['positions'])

        if ((self.matrix_test() != 1 and self.answer_line_type != "no") or
                (self.matrix_test() != 0 and self.answer_line_type == "no")):
            self.matrix = np.empty([self.n, self.n], dtype="unicode")
            self.matrix.fill('')
            self.fill_matrix(distractors)
        elif distractors:
            new_matrix = []
            for i in range(self.n):
                row = []
                for c in range(self.n):
                    row.append(random.choice(ALPHABET)[0] + self.matrix[i, c])
                new_matrix.append(row)
            self.matrix = np.asarray(new_matrix)

    def matrix_test(self):
        lines = self.get_all_lines()
        lines_without_duplicates = 0
        for line in lines:
            if len(set(line['values'])) == self.n:
                lines_without_duplicates += 1
        return lines_without_duplicates

    def __get_line_exceptions(self, line_type, line_number):
        if line_type not in ALL_LINES:
            logging.error(line_type + " is wrong name for line")
            raise Exception(line_type + " is wrong name for line")
        elif line_number < 0 or line_number >= self.n:
            logging.error("type has to by between [0, n)")
            raise Exception("type has to by between [0, n)")
        elif line_type == 'diagonal' and line_number not in [0, 1]:
            logging.error("for diagonal line number must be 0 or 1")
            raise Exception("for diagonal line number must be 0 or 1")

    def get_line_values(self, line_type, line_number):
        self.__get_line_exceptions(line_type, line_number)

        if line_type == 'row':
            return deepcopy(self.matrix[line_number])
        elif line_type == 'column':
            return deepcopy(self.matrix[:, line_number])
        elif line_type == 'diagonal' and line_number == 0:
            return deepcopy(self.matrix[range(self.n), range(self.n)])
        elif line_type == 'diagonal' and line_number == 1:
            return deepcopy(self.matrix[range(self.n), range(self.n - 1, -1, -1)])
        else:
            logging.error("something unexpected in Matrix.get_line_values :(")
            raise Exception("something unexpected in Matrix.get_line_values :(")

    def get_line_positions(self, line_type, line_number):
        self.__get_line_exceptions(line_type, line_number)

        if line_type == 'row':
            return np.array([[line_number, i] for i in range(self.n)])
        elif line_type == 'column':
            return np.array([[i, line_number] for i in range(self.n)])
        elif line_type == 'diagonal' and line_number == 0:
            return np.array([[i, i] for i in range(self.n)])
        elif line_type == 'diagonal' and line_number == 1:
            return np.array([[i, self.n - 1 - i] for i in range(self.n)])
        else:
            logging.error("something unexpected in Matrix.get_line_positions :(")
            raise Exception("something unexpected Matrix.get_line_positions :(")

    def get_all_lines(self):
        all_lines = []
        for line_type in [elem for elem in self.possible_answers if elem != 'no']:
            for line_number in range(self.n):
                line_positions = self.get_line_positions(line_type, line_number)
                line_values = self.get_line_values(line_type, line_number)
                line_filling = len([elem for elem in line_values if elem != ''])
                all_lines.append({"type": line_type, "number": line_number, "filling": line_filling,
                                  "positions": line_positions, "values": line_values})
                if line_type == 'diagonal' and line_number == 1:
                    break
        return all_lines

    def get_all_lines_sorted(self):
        return sorted(self.get_all_lines(), key=lambda k: k['filling'], reverse=True)

    def get_all_lines_to_fill(self):
        return [line for line in self.get_all_lines_sorted() if line['filling'] < self.n]

    def get_line_to_fill(self):
        lines_to_fill = self.get_all_lines_to_fill()

        if len(lines_to_fill) == 0:
            return []

        for line in lines_to_fill:
            # if there is no duplicates
            if len(set(line['values'])) - 1 == line['filling']:
                return line
        return lines_to_fill[0]

    # --------------- Matrix info ------------------ #
    def get_info(self):
        info = {'matrix': self.matrix,
                'N': self.n,
                'possible_answers': self.possible_answers,
                'answer_line_type': self.answer_line_type,
                'answer_line_number': self.answer_line_number}

        return info
