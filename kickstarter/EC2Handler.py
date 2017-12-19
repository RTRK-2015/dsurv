import boto3


class EC2Handler:

    def __init__(self):
        self.c = boto3.client("ec2")

    def run(self, ami, i_type, user_data, keypair, name):
        response = self.c.run_instances(
            DryRun=False,
            ImageId=ami,
            InstanceType=i_type,
            KeyName=keypair,
            TagSpecifications=[{
                "ResourceType": "instance",
                "Tags": [{
                    "Key": "Name",
                    "Value": name
                }]

            }],
            MaxCount=1,
            MinCount=1,
            SecurityGroups=["sg_mrkirm2"],
            UserData=user_data
        )
        return response

    def stop(self, instance_id):
        self.c.stop_instances(
            InstanceIds = [
                instance_id
            ]
        )

    def start(self, instance_id):
        self.c.start_instances(
            InstanceIds = [
                instance_id
            ]
        )

    def term(self, instance_id):
        self.c.terminate_instances(
            InstanceIds = [
                instance_id
            ]
        )

    def desc(self):
        response = self.c.describe_instances()

        info = []
        #InstanceId, ImageId, InstanceType, State, PrivateIpAddress, PublicIpAddress.

        for reservations in response["Reservations"]:
            for instances in reservations["Instances"]:
                info.append({
                    "InstanceId" : instances["InstanceId"],
                    "ImageId" : instances["ImageId"],
                    "InstanceType" : instances["InstanceType"],
                    "State" : instances["State"],
                    "PrivateIpAddress" : "None",
                    "PublicIpAddress" : "None"
                })

                if instances["State"]["Name"] != "terminated":
                    info[-1]["PrivateIpAddress"] = instances["PrivateIpAddress"]

                if instances["State"]["Name"] == "running":
                    info[-1]["PublicIpAddress"] = instances["PublicIpAddress"]

        return info



