import boto3

lambda_client = boto3.client('lambda')
codepipeline_client = boto3.client('codepipeline')

def lambda_handler(event, context):
    try:
        ###
        # Get CodepipeLine Job ID
        ###
        
        job_id = event['CodePipeline.job']['id']
        
        ###
        # TODO implement
        ###

        ### 
        # Response job result(success) to codepipeline
        ###
        
        codepipeline_client.put_job_success_result(jobId=job_id)            
     
    except Exception as e:
        ### 
        # Response job result(failure) to codepipeline
        ###

        codepipeline_client.put_job_failure_result(
            jobId=job_id,
            failureDetails={
                'type': 'JobFailed',
                'message': str(e)
        }
        ) 
        
        raise Exception(e)
