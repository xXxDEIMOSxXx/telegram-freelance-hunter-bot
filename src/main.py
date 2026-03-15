"""Main module"""

import asyncio

from src.bootstrap import bootstrap


async def main():
    """Main function"""

    await bootstrap()


if __name__ == "__main__":
    asyncio.run(main())
