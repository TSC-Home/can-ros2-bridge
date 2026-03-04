FROM ros:humble

RUN apt-get update && apt-get install -y \
    curl build-essential python3-pip iproute2 \
    libclang-dev clang \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip3 install cantools lxml click pytest

WORKDIR /ws
COPY . /ws

SHELL ["/bin/bash", "-c"]
RUN source /opt/ros/humble/setup.bash && cd node && cargo build --release --features ros2
