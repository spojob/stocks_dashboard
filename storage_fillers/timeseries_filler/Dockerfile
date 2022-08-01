FROM python:3.9-slim
COPY . ./

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt
WORKDIR ./
CMD ["/run.sh"]