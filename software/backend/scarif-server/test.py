import logging
from rich.logging import RichHandler
from managers.cienciomanager import CiencioManager
from entities.scarifentities import *
from rich import print,inspect
from rich.console import Console


def main():
    console = Console()
    console.clear()

    FORMAT = "%(message)s"
    
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
    log = logging.getLogger("rich")
    km = CiencioManager()
    
    try:
        print()

    except Exception as e:
        inspect (e)
        log.exception(e)

if __name__ == '__main__':
    main()