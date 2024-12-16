# -*- coding: utf-8 -*-
import datetime
import random


def generate_ipv4():
    """Generate a random IPv4 address."""
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))


def generate_request(url):
    """Generate a random HTTP request."""
    methods = ["GET", "POST", "PUT", "DELETE"]
    protocol = "HTTP/1.1"
    method = random.choice(methods)
    return f'"{method} {url} {protocol}"'


def generate_user_agent():
    """Generate a random User-Agent string."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
    ]
    return random.choice(user_agents)


def generate_timestamp():
    """Generate the current timestamp in the log format."""
    return datetime.datetime.utcnow().strftime('%d/%b/%Y:%H:%M:%S +0800')  # +0800 is the time zone offset for China


def generate_log_entry():
    """Generate a single log entry."""
    source_ip = generate_ipv4()
    url = random.choice(["/index.html", "/login", "/home", "/about", "/contact"])
    status = random.choice([200, 403, 404, 500])
    body_bytes_sent = random.randint(500, 5000)
    user_agent = generate_user_agent()

    log_entry = f'{source_ip} - - [{generate_timestamp()}] {generate_request(url)} {status} {body_bytes_sent} "-" "{user_agent}"'
    return log_entry


def write_logs(filename, total_logs=100):
    """Write generated logs to a file."""
    with open(filename, 'a', encoding='utf-8') as f:
        for _ in range(total_logs):
            log_entry = generate_log_entry()
            f.write(log_entry + '\n')


if __name__ == "__main__":
    log_file = 'generated_logs.txt'
    write_logs(log_file, total_logs=2000)  # Change the number of logs if needed
    print(f"Logs have been written to {log_file}")
