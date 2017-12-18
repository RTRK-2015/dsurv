import argparse

from client.Client import Client


def parse():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input_file",
        help="the name of the file to be processed",
        default="client_main.py"
    )

    parser.add_argument(
        "-c",
        "--cli_q",
        help="the name of the client queue",
        default="dsurv-client-queue"
    )

    parser.add_argument(
        "-s",
        "--srv_q",
        help="the name of the server queue",
        default="server-input"
    )

    parser.add_argument(
        "-b",
        "--srv_b",
        help="the name of the server bucket",
        default="titos-treasury"
    )

    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        help="the switch whether to send a file request or direct request",
        action="store_true",
        default=True
    )

    parser.add_argument(
        "-d",
        "--direct",
        dest="file",
        help="the switch to send a direct request",
        action="store_false",
        default=False
    )

    parser.add_argument(
        "-l",
        "--list",
        nargs='*',
        help="the list of words to count"
    )

    return parser.parse_args()


def main():
    args = parse()

    print(args)
    print(args.list)

    input_file = args.input_file
    cli_q_name = args.cli_q
    srv_q_name = args.srv_q
    srv_b_name = args.srv_b
    is_file = args.file
    words = args.list

    with Client(
            cli_q_name=cli_q_name,
            srv_q_name=srv_q_name,
            srv_b_name=srv_b_name
    ) as cli:
        cli.run(
            is_file=is_file,
            words=words,
            input_file=input_file
        )


if __name__ == '__main__':
    main()