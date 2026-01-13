FROM golang:1.21-alpine

WORKDIR /app

# Copy dependency files dulu (INI WAJIB)
COPY go.mod go.sum ./

# Download semua dependency
RUN go mod download

# Copy seluruh source code
COPY . .

# Build binary
RUN go build -o main .

EXPOSE 8081
CMD ["./main"]
