# ── Stage 1: Build Spring Boot JAR ─────────────────────────────────────────
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

# ── Stage 2: Final image with Java + Python ─────────────────────────────────
FROM eclipse-temurin:17-jre
WORKDIR /app

# Install Python3 + pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy ML folder and install Python dependencies
COPY ml/ ./ml/
RUN pip3 install -r ml/requirements.txt --break-system-packages

# Copy Spring Boot JAR from build stage
COPY --from=build /app/target/*.jar app.jar

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8080

ENTRYPOINT ["./start.sh"]