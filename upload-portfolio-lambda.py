import boto3
import StringIO
import zipfile
import mimetypes
def lambda_handler(event, context):
    sns=boto3.resource('sns',region_name="us-east-1")
    s3=boto3.resource('s3')

    topic=sns.Topic('arn:aws:sns:us-east-1:760080144293:deployPortfolioTopic')
    location={
    "bucketName":"portfoliobuild.akshay.biz",
    "objectKey":"portfoliobuild.zip"

    }
    try:
        job=event.get("CodePipeline.job")
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"]=="MyAppBuild":
                    location=artifact["location"]["s3Location"]

        print "Building Portfolio from " + str(location)
        portfolio_bucket=s3.Bucket('portfolio.akshay.biz')
        build_bucket=s3.Bucket(location["bucketName"])

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"],portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj=myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Subject="Portfolio" , Message="Portfolio Deployed Successfully")
        if job:
            codepipeline=boto3.client('codepipeline',region_name="ap-south-1")
            codepipeline.put_job_success_result(jobId=job["id"])
    except:
        topic.publish(Subject="Portfolio Deploy Failed",Message="The portfolio was not deployed successfully")
        raise
    return "Hello From Lambda"
