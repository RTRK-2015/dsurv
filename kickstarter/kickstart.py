import argparse
import re

from kickstarter.EC2Handler import EC2Handler


def regex_magic(acs_key, sec_acs_key, data):
    data = re.sub("{ACCESS_KEY}", acs_key, data)
    data = re.sub("{SECRET_ACCESS_KEY}", sec_acs_key, data)

    return data


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--start",
        dest="start",
        action="store_true",
        help="the switch to start an ec2_instance running the server app",
        default=True
    )

    parser.add_argument(
        "-d",
        "--delete",
        dest="start",
        action="store_false",
        help="the switch to delete the running ec2_instance running the server app",
        default=False
    )

    parser.add_argument(
        "-i",
        "--input",
        help="name of the init script",
        default="ec2_init.sh"
    )

    parser.add_argument(
        "-n",
        "--name",
        help="Instance name",
        default="Jadranka"
    )
    parser.add_argument(
        "-k",
        "--key",
        help="key pair name",
        default="aws-dsurv-key"
    )

    parser.add_argument(
        "-u",
        "--unique_id",
        help="the ec2 instance unique id"
    )

    parser.add_argument(
        "-a",
        "--ami",
        help="the AMI used by the ec2 instance",
        default="ami-bf2ba8d0"
    )

    parser.add_argument(
        "-t",
        "--type",
        help="the type of the ec2 instance",
        default="t2.micro"
    )

    parser.add_argument(
        "-c",
        "--access_key",
        help="the aws access key",
        required=True
    )

    parser.add_argument(
        "-x",
        "--secret_access_key",
        help="the aws secret access key",
        required=True
    )

    return parser.parse_args()


def get_as_user_data(filename):
    with open(filename, "r") as f:
        return f.read()


def start(args):
    if args.ami != "ami-bf2ba8d0" or args.type != "t2.micro":
        print("MONEY MONEY MONEY")
        raise Exception("MONEY MONEY MONEY")

    user_data = regex_magic(
        data=get_as_user_data(args.input),
        acs_key=args.access_key,
        sec_acs_key=args.secret_access_key
    )

    handler = EC2Handler()

    res = handler.run(
        ami=args.ami,
        i_type=args.type,
        user_data=user_data,
        keypair=args.key,
        name=args.name
    )

    print(res)
    i_id = res["Instances"][0]["InstanceId"]
    print(i_id)
    waiter = handler.c.get_waiter("instance_running")
    print("Starting waiting")
    waiter.wait(InstanceIds=[i_id])
    print("Finished waiting on create")

    print("writing id to file")
    with open("instance_id.txt", "w") as f:
        f.write(i_id)


def stop(args):

    handler = EC2Handler()

    with open("instance_id.txt", "r") as f:
        i_id = f.read()

    handler.term(i_id)


def main():
    args = parse()
    print(args)
    print(args.start)

    is_start = args.start

    if is_start:
        start(args)
    else:
        stop(args)


if __name__ == '__main__':
    main()