import boto3


# Class that provides a more high-level interface to S3.
class S3:
    # Constructs a bucket either by creating a new bucket, or opening it, if it already exists.
    def __init__(self, name):
        self.client = boto3.client("s3")
        self.name = name

        response = self.client.list_buckets()
        if "Buckets" in response:
            buckets = response["Buckets"]
            count = sum(1 for bucket in buckets if bucket["Name"] == name)
            if count > 0:
                return

        self.client.create_bucket(
            ACL="public-read-write",
            Bucket=name,
            CreateBucketConfiguration={
                "LocationConstraint": "eu-central-1"
            }
        )

    def __enter__(self):
        return self

    # Deletes the bucket
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__destroy_contents(self.name)
        self.client.delete_bucket(
            Bucket=self.name
        )

    # Helper function to delete all objects in a bucket.
    def __destroy_contents(self, bucket_name):
        response = self.client.list_objects_v2(
            Bucket=bucket_name,
        )

        #while response['KeyCount'] > 0:
        if response['KeyCount'] > 0:
            self.client.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects': [{'Key': obj['Key']} for obj in response['Contents']]
                }
            )

    # Function that uploads a local file to the bucket.
    def upload(self, local_file, remote_file):
        self.__wait_exists()
        with open(local_file, "rb") as data:
            self.client.upload_fileobj(
                Fileobj=data,
                Bucket=self.name,
                Key=remote_file
            )

    # Function that downloads a remote bucket file to the computer.
    def download(self, local_file, remote_file):
        self.__wait_exists()
        with open(local_file, "wb") as data:
            self.client.download_fileobj(
                Bucket=self.name,
                Key=remote_file,
                Fileobj=data
            )

    # Function that deletes a remote file from a bucket.
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

    @staticmethod
    def destroy(bucket_name):
        client = boto3.client("s3")
        client.delete_bucket(
            Bucket=bucket_name
        )
