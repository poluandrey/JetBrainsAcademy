import argparse
import json
import io
import random

from pathlib import Path


class StringBuf:

    def __init__(self):
        self.buffer = io.StringIO()

    def info(self, message):
        print(message)
        self.buffer.write(str(message))

    def save_to_file(self, filename):
        with open(filename, 'w') as f_in:
            f_in.write(self.buffer.getvalue())


class DefinitionAlreadyExistError(Exception):
    def __init__(self, definition):
        self.definition = definition

    def __str__(self):
        return f'The definition "{self.definition}" already exists. Try again:'


class TermAlreadyExistError(Exception):
    def __init__(self, term):
        self.term = term

    def __str__(self):
        return f'The term "{self.term}" already exists. Try again:'


class CardDoesNotExistError(Exception):
    def __init__(self, term):
        self.term = term

    def __str__(self):
        return f'Can\'t remove "{self.term}": there is no such card.'


class FlashCard:

    def __init__(self):
        self.cards = {}
        self.hardest_cards = {}

    def add_card(self, term, definition):
        """add new card"""
        self.cards[term] = definition
        logger.info(f'The pair ("{term}":"{definition}") has been added')

    def remove_card(self, term):
        if term not in self.cards.keys():
            raise CardDoesNotExistError(term)
        del self.cards[term]

    def import_from_file(self, file):
        with open(file, 'r') as f_in:
            cards_from_file = json.load(f_in)
        term_for_del = set.intersection(set(self.cards.keys()), set(cards_from_file.keys()))
        if term_for_del:
            for term in term_for_del:
                self.remove_card(term)
        for term, definition in cards_from_file.items():
            self.cards[term] = definition
        logger.info(f'{len(cards_from_file)} cards have been loaded.')

    def export_to_file(self, file):
        with open(file, 'w') as f_in:
            json.dump(self.cards, f_in)
        logger.info(f'{len(self.cards)} cards have been saved\n')

    def add_hard_card(self, term):
        if term in self.hardest_cards.keys():
            self.hardest_cards[term] += 1
        else:
            self.hardest_cards[term] = 1

    def print_hardest_cards(self):
        if not self.hardest_cards:
            logger.info('There are no cards with errors.')
            return
        max_error_cnt = max(self.hardest_cards.values())
        hardest_term = [f'"{x}"' for x in (filter(lambda x: self.hardest_cards[x] == max_error_cnt, self.hardest_cards.keys()))]
        hardest_term = ', '.join(hardest_term)
        # logger.info(hardest_term)
        if ',' not in hardest_term:
            logger.info(f'The hardest card is {hardest_term}. You have {max_error_cnt} errors answering it.')
        else:
            logger.info(f'The hardest cards are {hardest_term}. You have {max_error_cnt} errors answering them.')

    def reset_stats(self):
        self.hardest_cards = {}
        logger.info('Card statistics have been reset\n')


def ask_question(card: FlashCard):
    logger.info('How many times to ask?')
    question_cnt = int(input())
    logger.info(question_cnt)
    for _ in range(question_cnt):
        term = random.choice(list(card.cards.keys()))
        definition = card.cards[term]
        logger.info(f'Print the definition of "{term}"')
        answer = input()
        logger.info(answer)
        if answer == definition:
            logger.info('Correct')
        elif answer != definition and answer in card.cards.values():
            card.add_hard_card(term)
            another_term = [term for term, definition in card.cards.items() if definition == answer][0]
            logger.info(f'Wrong. The right answer is "{definition}", but '
                        f'your definition is correct for "{another_term}".')
        else:
            logger.info(f'Wrong. The right answer is "{definition}"')
            card.add_hard_card(term)


def remove_card(card: FlashCard):
    logger.info('Which cars?\n')
    card_for_remove = input('Which card?\n')
    try:
        card.remove_card(card_for_remove)
    except CardDoesNotExistError as err:
        print(err)


def play_game(card: FlashCard, args):
    # print('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):\n')
    logger.info('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):')
    action = input()
    logger.info(action)
    if args.import_from:
        card.import_from_file(args.import_from)

    if action == 'exit':
        if args.export_to:
            card.export_to_file(args.export_to)
        logger.info('bye bye')
        return False
    if action == 'add':
        logger.info('The term for card')
        while True:
            term = input()
            logger.info(term)
            try:
                if term in card.cards.keys():
                    raise TermAlreadyExistError(term)
                break
            except TermAlreadyExistError as err:
                logger.info(err)
        logger.info('The definition for card')
        while True:
            definition = input()
            logger.info(definition)
            try:
                if definition in card.cards.values():
                    raise DefinitionAlreadyExistError(definition)
                break
            except DefinitionAlreadyExistError as err:
                logger.info(err)
        card.add_card(term, definition)
    elif action == 'ask':
        ask_question(card)
    elif action == 'remove':
        remove_card(card)
        logger.info('The card has been removed.')
    elif action == 'export':
        logger.info('File name:')
        file = input()
        logger.info(file)
        card.export_to_file(file)
    elif action == 'import':
        logger.info('File name:')
        file = input()
        logger.info(file)
        if not Path(file).exists():
            logger.info('File not found')
            return True
        card.import_from_file(file)
    elif action == 'log':
        logger.info('File name:')
        filename = input()
        logger.save_to_file(filename=filename)
        logger.info('The log has been saved.')
    elif action == 'hardest card':
        card.print_hardest_cards()
    elif action == 'reset stats':
        card.reset_stats()
    return True




def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--import_from', required=False)
    parser.add_argument('--export_to', required=False)
    return parser.parse_args()



if __name__ == "__main__":
    card = FlashCard()
    logger = StringBuf()
    args = argument_parser()
    game = True
    while game:
        game = play_game(card, args)
