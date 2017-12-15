import boto3


class S3:
    def __init__(self, name):
        self.client = boto3.client("s3")
        self.name = name

        self.client.create_bucket(
            ACL="public-read-write",
            Bucket=name,
            CreateBucketConfiguration={
                "LocationConstraint": "eu-central-1"
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.delete_bucket(
            Bucket=self.name
        )

    def upload(self, local_file, remote_file):
        self.__wait_exists()
        with open(local_file, "rb") as data:
            self.client.upload_fileobj(
                Fileobj=data,
                Bucket=self.name,
                Key=remote_file
            )

    def download(self, local_file, remote_file):
        self.__wait_exists()
        with open(local_file, "wb") as data:
            self.client.download_fileobj(
                Bucket=self.name,
                Key=remote_file,
                Fileobj=data
            )

    def delete(self, remote_file):
        self.__wait_exists()
        self.client.delete_object(
            Bucket=self.name,
            Key=remote_file
        )

    def __wait_exists(self):
        waiter = self.client.get_waiter("bucket_exists")
        waiter.wait(
            Bucket=self.name,
            WaiterConfig={
                "Delay": 2,
                "MaxAttempts": 5
            }
        )

