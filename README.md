# SDS-in-a-box

Hello!  This a project that attempts to capture the minimum requirements for the core of a Science Data System.  

Our goal with the project is that users will only need to modify the file config.json to define the data products stored on the SDC, and the rest should be mission agnostic.  

## Architecture

The code in this repository takes the form of an AWS CDK project. It provides the architecture for:

1. An HTTPS API to upload files to an S3 bucket
2. An S3 bucket to contain uploaded files
3. An HTTPS API to query and download files from the S3 bucket
4. A lambda function that inserts file metadata into an openseach instance


## Development

The development environment uses a GitHub codespace, to ensure that we're all using the proper libraries as we develop and deploy.  

Everyone gets 50 free hours per month of github Codespace time.  Alternatively, your organization can pay for it to run longer than this.  

Top start a new development environment, click the button for "Code" in the upper right corner of the repository, and click "Codespaces".  

### AWS Setup
The first thing you'll need to do is configure your aws environemnt with:

```
aws configure
```

Enter in your AWS Access Key ID and AWS Secret Access Key, which can be obtained by setting up a user account in the AWS console. For region, set it to the AWS region you'd like to set up your SDS.  For IMAP, we're using "us-west-2"

**NOTE**-- If this is a brand new AWS account, then you'll need to bootstrap your account to allow CDK deployment with the command: 

```
cdk bootstrap
```

### Deploy

To deploy the SDS, first you'll need to snyth the CDK code with the command:

```
cdk synth
```

and then you can deploy the architecture with the following command:

```
cdk deploy
```



