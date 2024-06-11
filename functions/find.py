import logging

from pretty_utils.type_functions.lists import split_list
from pretty_utils.type_functions.strings import format_number

from data import config
from functions.General import General
from utils.db_api.database import db, get_addresses
from utils.db_api.models import EligibleAddress, Address


def find() -> None:
    try:
        if not db.one(EligibleAddress):
            print(f'{config.RED}Start parsing eligible addresses first!{config.RESET_ALL}')
            return

        try:
            open(file=config.ADDRESSES_FILE, mode='r+')

        except IOError:
            print(f"{config.RED}You didn't close the {config.ADDRESSES_FILE} file!{config.RESET_ALL}")
            return

        print(f'Importing addresses from the spreadsheet to DB...')
        General.import_addresses()

        specified_addresses = get_addresses()
        if not specified_addresses:
            print(f"{config.RED}You didn't specify a single address!{config.RESET_ALL}")
            return

        print('N\t' + '\t'.join(list(db.execute('SELECT * FROM addresses').keys())[1:]))
        total_amount = 0
        n = 1
        for address_list in split_list(s_list=specified_addresses, n=100):
            for address_instance in address_list:
                eligible_address_instance = db.one(EligibleAddress, EligibleAddress.address == address_instance.address)
                if eligible_address_instance:
                    address_instance.amount = eligible_address_instance.amount
                    total_amount += eligible_address_instance.amount

                print(f'{n}\t{address_instance.address}\t{address_instance.amount}')
                n += 1

            db.commit()

        eligible_addresses = db.all(Address, Address.amount != 0)
        average_points = round(total_amount / len(eligible_addresses)) if eligible_addresses else 0
        print(f'''

Eligible addresses: {config.LIGHTGREEN_EX}{format_number(len(eligible_addresses))}/{format_number(len(specified_addresses))} ({round(len(eligible_addresses) / len(specified_addresses) * 100, 2)}%){config.RESET_ALL}
Total points: {config.LIGHTGREEN_EX}{format_number(total_amount)}{config.RESET_ALL}
Average points: {config.LIGHTGREEN_EX}{format_number(average_points)}{config.RESET_ALL}''')

        General.export_addresses()
        db.execute('DROP TABLE addresses')

    except BaseException as e:
        logging.exception('find')
        print(f"\n{config.RED}Something went wrong in the 'find' function: {e}{config.RESET_ALL}\n")
