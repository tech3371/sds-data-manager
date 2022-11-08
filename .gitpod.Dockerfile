FROM gitpod/workspace-full-vnc
RUN sudo apt-get update && \
    sudo apt-get install -y libgtk-3-dev
RUN sudo apt install -y nodejs
RUN npm install -g aws-cdk
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN sudo ./aws/install
RUN export AWS_CONFIG_FILE=/workspace/SDS-in-a-box/.aws/config
RUN export AWS_SHARED_CREDENTIALS_FILE=/workspace/SDS-in-a-box/.aws/credentials