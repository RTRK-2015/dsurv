destroy()
{
	for bucket in $(python ./aws s3 ls | cut -d" " -f 3 | tr -d '\r')
	do
		python ./aws s3 rb --force s3://$bucket
	done
}

destroy