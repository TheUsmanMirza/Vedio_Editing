import os
import boto3
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)


# function to check file extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# s3://videos-editor/videos/
# access key id: AKIARPGOCGXSXIFWHPOI
# secret access key: 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


def upload_file_to_s3(file,f_name, acl="public-read", directory="videos"):
    f = open(file, 'r')
    file_name = f.name.split('/')[-1]
    try:
        s3.upload_file(
            Filename=file,
            Bucket=os.getenv("AWS_BUCKET_NAME"),
            Key='videos/' + f_name,
        )
        url = 'https://{}.s3.amazonaws.com/{}'.format(os.getenv("AWS_BUCKET_NAME"), "{}/{}".format(directory, f_name))
        # url = signed_url(url, directory="videos")
        return url

    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e

    # after upload file to s3 bucket, return filename of the uploaded file
    # return file.filename


def signed_url(url, directory):
    """
    returns the signed(public) url for S3 bucket object.
    """
    public_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.getenv("AWS_BUCKET_NAME"), 'Key': "{}/{}".format(directory, os.path.basename(url))},
        ExpiresIn=604800
    )
    return public_url
