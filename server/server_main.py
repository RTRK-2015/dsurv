from argparse import ArgumentParser

from server.Server import Server


def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        "-b",
        "--bucket",
        help="Name of the server bucket",
        default="titos-treasury"
    )

    parser.add_argument(
        "-q",
        "--queue",
        help="name of server queue",
        default="server-input"
        )

    return parser.parse_args()


def main():
    args = parse_args()

    with Server(args.queue, args.bucket) as srv:
        srv.run()


if __name__ == '__main__':
    main()
