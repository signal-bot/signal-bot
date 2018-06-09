#!/usr/bin/env python3
from argparse import ArgumentParser
from signalbot import Signalbot

parser = ArgumentParser(description='Signalbot')
parser.add_argument('--data-dir', help='Data and config directory')
parser.add_argument('--mocker', action='store_true', default=False)

args = parser.parse_args()

bot = Signalbot(data_dir=args.data_dir, mocker=args.mocker)
bot.start_and_wait()
