# Democast

Show Demo videos live in your Webex Meetings!
<!--[![Vidcast Overview](https://github.com/wxsd-sales/custom-pmr-pin/assets/19175490/4861e7cd-7478-49cf-bada-223b30810691)](https://app.vidcast.io/share/3f264756-563a-4294-82f7-193643932fb3)-->
<!--[![Vidcast Overview](https://github-production-user-asset-6210df.s3.amazonaws.com/19175490/249649420-980de741-1a2c-4aea-883e-4da629bc8701.png)](https://app.vidcast.io/share/677cc9bc-b0bb-4419-9338-5f4bbe0100a3)-->

<!--## Overview-->

<!--### Flow Diagram-->
<!--![PSTN Flow](https://github.com/wxsd-sales/custom-pmr-pin/assets/19175490/bb4d0ed9-7d57-4306-ae99-74d37337a562)-->


## Setup

### Prerequisites & Dependencies:

- Developed on MacOS Ventura (13.2.1) & Ubuntu Bionic (18.04)
- Developed on Python 3.8.1 & 3.8.3
-   Other OS and Python versions may work but have not been tested

### AWS CLI Config & Usage
I've sent each of use access keys for the AWS CLI.  You likely **already have** access keys setup for DJ's environment, so I recommend you do **NOT** overwrite those with these new ones. Otherwise you might have to go hunting or ask DJ for your credentials again.  Instead, I recommend you configure a second profile like so:

```
aws configure —profile account2  
```
Above, I have named my profile for **our** AWS environment `account2`.  You can name it something else, but be mindful of what you pick for the remaining commands.  Note, you will use the same `—profile account2` argument for all of your typical commands.  For example:

```
aws ecr get-login-password --region us-west-1 --profile account2 | docker login --username AWS --password-stdin 134113390236.dkr.ecr.us-west-1.amazonaws.com
aws ecr create-repository --repository-name EXAMPLE --profile account2 
```

If you look closely, the account number in the login command above is 134113390236, which is different from the AWS Account ID for DJ's environment.  If you use your default profile to log into **our** AWS environment (134113390236) you will likely hit a bunch of permission denied errors if you try to do anything like create or push repos for obvious reasons.

If you use `—profile account2` to log into DJ's AWS accountId (191518685251) you will also not be able to do anything for the same reason.

At this point, it should be clear that the above commands, as well as the remaining commands you use to push your docker containers are identical to what you already do for DJ's environment.  The only differences for our environment are:

1. Use, `—profile account2` for any `aws` cli commands (aws configure, aws ecr, etc)
2. Use 134113390236 as the account ID for the ECR (repo) mostly in the docker command line commands.  Examples:

```
docker tag democast:latest 134113390236.dkr.ecr.us-west-1.amazonaws.com/democast:latest
docker push 134113390236.dkr.ecr.us-west-1.amazonaws.com/democast:latest  
```

### AWS Console/UI

Now, the major difference is how we deploy and manage our services in AWS.  DJ's environment uses Kubernetes (EKS).  Our environment uses Amazon's custom implementation called ECS.  The major reason for this is Kubernetes costs extra.

This means you can't use kubectl to create and interact with your services.   HOWEVER, you can deploy them entirely from the AWS console UI, which is nice, and I've given you all admin access to:
https://cloudsso.cisco.com/idp/startSSO.ping?PartnerSpId=https://signin.aws.amazon.com/saml
Note I recommend you bookmark the above URL as is.  If you try to bookmark aws.amazon.com after you sign in, you'll get taken to a page asking for a username and password which you do not have because we sign in with our CEC using SSO.

### AWS Service Management/Restart

The bulk of how to manage and deploy a new container service to our AWS environment (134113390236) using the AWS console UI will be covered in the meeting recording.

However, you probably use Lens to restart your deployments today, which is convenient.  While it is possible to deploy a new service from the aws cli using `aws ecs`, I don't use it, and therefore I don't know how to do it.  I always login to the AWS console UI.

That said, it is pretty annoying to login to AWS just to restart a service after you've pushed it with a `docker push` command.  So, I DO know how to **restart** a service from the command line:

```
aws ecs update-service --force-new-deployment --service democast-service --cluster WXSD-Main --profile account2 
```
1. Note the use of —profile account2 once again here because this is an `aws` command
2. Note the cluster name - if you are using the cluster I've already setup (recommended), then this should be the same as the above example.
3. Note the service name - this will change for each service.  It also may not match the ECR repo, so you need to be mindful of what you are naming your services.

### EFS File Management for Media (.mjpeg/.wav)

If you need to add files to the EFS for democast, you can SSH into an EC2 I setup specifically for this:
```
ssh -i "efs.pem" ec2-user@ec2-18-144-6-188.us-west-1.compute.amazonaws.com  
```
Note, I run the ssh command from the directory where I have saved `efs.pem`.  Otherwise you'll need to provide the appropriate path there.
If this command works for you, then I'd recommend using Cyberduck to SFTP upload any new .mjpeg or .wav files. 

If somehow, the EFS becomes unmounted or corrupt, you can mount a new one FROM the EC2 instance (SSH into it with above command, changing hostname if EC2 box changes or its IP changes) with this command:
```
sudo mount -t nfs -o nfsvers=4,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport fs-00289f6142d5d35c9.efs.us-west-1.amazonaws.com:/  efs-mount 
```
Note the EFS DNS name in the above command - if you create a new EFS for some reason, make sure to replace it in the above command.

<!-- GETTING STARTED -->

### Installation Steps:

1.  Right now, this pretty much only works inside a docker container.

    
## Live Demo

<!-- Update your vidcast link -->
<!--Check out our Vidcast recording, [here](https://app.vidcast.io/share/3f264756-563a-4294-82f7-193643932fb3)!-->

<!-- Keep the following statement -->
*For more demos & PoCs like this, check out our [Webex Labs site](https://collabtoolbox.cisco.com/webex-labs).

## License

All contents are licensed under the MIT license. Please see [license](LICENSE) for details.

## Disclaimer

<!-- Keep the following here -->  
Everything included is for demo and Proof of Concept purposes only. Use of the site is solely at your own risk. This site may contain links to third party content, which we do not warrant, endorse, or assume liability for. These demos are for Cisco Webex usecases, but are not Official Cisco Webex Branded demos.
 
 
## Support

Please contact the Webex SD team at [wxsd@external.cisco.com](mailto:wxsd@external.cisco.com?subject=CustomPMRPIN) for questions. Or for Cisco internal, reach out to us on Webex App via our bot globalexpert@webex.bot & choose "Engagement Type: API/SDK Proof of Concept Integration Development". 
