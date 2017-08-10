rm -r aws-lambda-s3-thumbnail.zip
cd aws-lambda-s3-thumbnail/

rm -rf venv
virtualenv venv
source venv/bin/activate
pip install -r requirement.txt

zip -9 ../aws-lambda-s3-thumbnail.zip handler.py
cd venv/lib/python2.7/site-packages/
zip -r9 ../../../../../aws-lambda-s3-thumbnail.zip *
cd ../../../../../

bucket_name="upload-image"

echo '{
    "LambdaFunctionConfigurations": [
        {
            "LambdaFunctionArn": "<lambda_function_arn>",
            "Id": "aws-object-created-id",
                "Events": [
                    "s3:ObjectCreated:*"
                ]
        },
        {
            "LambdaFunctionArn": "<lambda_function_arn>",
            "Id": "aws-object-removed-id",
            "Events": [
                "s3:ObjectRemoved:*"
            ]
        }
    ]
}' > notification.json

serverless deploy
aws lambda add-permission --function-name <lambda_function_arn> --statement-id 1 --action "lambda:InvokeFunction" --principal "s3.amazonaws.com" --source-arn "arn:aws:s3:::${bucket_name}"
aws s3api put-bucket-notification-configuration --bucket ${bucket_name} --notification-configuration file://notification.json
