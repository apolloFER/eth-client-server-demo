FROM golang:1.8

WORKDIR /go/src/eth
COPY eth/ .

RUN go-wrapper download   # "go get -d -v ./..."
RUN go-wrapper install    # "go install -v ./..."

COPY docker/start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]