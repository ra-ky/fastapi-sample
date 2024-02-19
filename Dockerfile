FROM python:3.12-slim

# bash 설정
RUN echo "alias egrep='egrep --color=auto'" >> ~/.bashrc
RUN echo "alias fgrep='fgrep --color=auto'" >> ~/.bashrc
RUN echo "alias grep='grep --color=auto'" >> ~/.bashrc
RUN echo "alias l='ls -CF'" >> ~/.bashrc
RUN echo "alias la='ls -A'" >> ~/.bashrc
RUN echo "alias ll='ls -alF'" >> ~/.bashrc
RUN echo "alias ls='ls --color=auto'" >> ~/.bashrc

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
