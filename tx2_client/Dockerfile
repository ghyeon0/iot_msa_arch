FROM openhorizon/aarch64-tx2-cudabase

RUN apt-get update && apt-get install -y \
  python3-pip \ 
  python3-dev \
  python3-numpy \
  python3-wheel 

RUN pip3 install --upgrade \
  pip \
  setuptools \
  https://github.com/peterlee0127/tensorflow-nvJetson/releases/download/binary/tensorflow-1.9.0-cp35-cp35m-linux_aarch64.whl

RUN rm -rf /var/cuda-repo-9-0-local/*.deb
RUN rm -rf /usr/local/cuda-9.0/doc/*
RUN rm -rf /root/src/jetsonhacks
RUN mv /usr/local/cuda-9.0/samples/2_Graphics/ /usr/local/cuda-9.0/
RUN rm -rf /usr/local/cuda-9.0/samples/*
RUN mv /usr/local/cuda-9.0/2_Graphics/ /usr/local/cuda-9.0/samples/

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "./main.py" ]
