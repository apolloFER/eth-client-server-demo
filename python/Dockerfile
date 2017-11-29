FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

ADD eth eth
ADD setup.py .

RUN pip install -e .

COPY docker/start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]