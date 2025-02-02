import argparse
import asyncio
import cProfile
import json

from DbInterface.Neo4jStreamAsync import Neo4jStreamAsync
from GraphModeler import import_database_json
from GraphModeler.DbTranformations.DbSaver import export_database_neo4j_async, delete_database_neo4j_async


def create_arg_parser() -> argparse.ArgumentParser:
    neo4j_parser = argparse.ArgumentParser()
    neo4j_parser.add_argument("--mode", "-m", choices=["export", "delete"], help="the mode of usage")
    neo4j_parser.add_argument("--username", "-u", help="the neo4j server username")
    neo4j_parser.add_argument("--password", "-p", help="the neo4j server password")
    neo4j_parser.add_argument("--address", "-a", help="the neo4j server address")
    neo4j_parser.add_argument("--database", "-d", help="a database file to load into neo4j", required=False)
    neo4j_parser.add_argument("--commit_size", "-c", help="the size of each commit to the database", required=False,
                              default=1000, type=int)
    neo4j_parser.set_defaults(func=neo4j_command)
    return neo4j_parser


def neo4j_command(args) -> None:
    """
    Handles the neo4j side of the cli
    :param args: the args from the command line
    """
    asyncio.run(run_command(args))


async def run_command(args):
    async with Neo4jStreamAsync(args.address, args.username, args.password, asyncio.get_event_loop()) as stream:
        if args.mode == "export":
            with open(args.database) as db_file:
                db_json = json.load(db_file)
            database = import_database_json(db_json)
            await export_database_neo4j_async(database, stream, 1000)
        elif args.mode == "delete":
            await delete_database_neo4j_async(stream)


def run():
    parser = create_arg_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    cProfile.run("run()")
