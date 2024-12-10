FROM python:3.12.6

ENV FORCE_COLOR=1

WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install -r requirements.txt
COPY . /bot
CMD python main.py 
