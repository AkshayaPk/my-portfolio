import boto3
import StringIO
import zipfile
import mimetypes
def lambda_handler(event, context):
    sns=boto3.resource('sns',region_name="us-east-1")
    s3=boto3.resource('s3')

    topic=sns.Topic('arn:aws:sns:us-east-1:760080144293:deployPortfolioTopic')

    try:
        portfolio_bucket=s3.Bucket('portfolio.akshay.biz')
        build_bucket=s3.Bucket('portfoliobuild.akshay.biz')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj=myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Subject="Portfolio" , Message="Portfolio Deployed Successfully")
    except:
        topic.publish(Subject="Portfolio Deploy Failed",Message="The portfolio was not deployed successfully")
        raise
    return "Hello From Lambda"
