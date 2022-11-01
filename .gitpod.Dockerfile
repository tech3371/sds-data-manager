FROM gitpod/workspace-full-vnc
RUN sudo apt-get update && \
    sudo apt-get install -y libgtk-3-dev
RUN sudo apt install -y nodejs
RUN npm install -g aws-cdk