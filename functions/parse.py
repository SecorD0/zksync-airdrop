import logging
import os
import urllib.request

from pretty_utils.miscellaneous.files import read_lines
from pretty_utils.type_functions.lists import split_list

from data import config
from utils.db_api.database import db
from utils.db_api.models import EligibleAddress, Base


def parse() -> None:
    try:
        if db.one(EligibleAddress):
            print(
                f"You've already parsed eligible addresses. Do you want to delete it and start over? "
                f"({config.LIGHTGREEN_EX}y{config.RESET_ALL}/{config.RED}n{config.RESET_ALL})"
            )
            answer = input('> ')
            print()
            if answer != 'y':
                return

            db.execute('DROP TABLE eligible_addresses')
            db.create_tables(Base)

        print(f'Downloading the CSV file with eligible addresses...')
        if not os.path.isfile(config.ELIGIBLE_ADDRESSES_FILE):
            urllib.request.urlretrieve(
                url='https://github.com/ZKsync-Association/zknation-data/raw/main/eligibility_list.csv',
                filename=config.ELIGIBLE_ADDRESSES_FILE
            )

        print(f'Importing addresses from the CSV file to the DB...')
        addresses = read_lines(path=config.ELIGIBLE_ADDRESSES_FILE)
        addresses = addresses[1:]
        total_addresses = len(addresses)
        address_lists = split_list(s_list=addresses, n=10_000)
        i = 0
        for address_list in address_lists:
            add_it = []
            for address in address_list:
                address = address.split(',')
                if not db.one(EligibleAddress, EligibleAddress.address == address[0]):
                    add_it.append(EligibleAddress(address=address[0], amount=address[1]))

                i += 1

            db.insert(add_it)
            print(f'{i}/{total_addresses}')

        print(f'A total of {config.LIGHTGREEN_EX}{i}{config.RESET_ALL} addresses were parsed.')

    except BaseException as e:
        logging.exception('parse')
        print(f"\n{config.RED}Something went wrong in the 'parse' function: {e}{config.RESET_ALL}\n")
