# def chunk_text(text, chunk_size=800):
#     chunks = []
#     start = 0

#     while start < len(text):
#         end = start + chunk_size
#         chunks.append(text[start:end])
#         start = end

#     return chunks




import re


def is_header_row(line: str) -> bool:
    keywords = ["g.q", "m.q", "nri", "quota", "lakhs", "$"]
    l = line.lower()
    return sum(k in l for k in keywords) >= 2


def extract_numbers(line: str):
    # Fix merged numbers like 4.6617.00 → 4.66 17.00
    line = re.sub(r"(\d)\.(\d{2})(\d{2})\.", r"\1.\2 \3.", line)
    return re.findall(r"\d+\.\d+", line)


def chunk_text(text: str):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    chunks = []
    headers = []
    current_headers = []

    for line in lines:
        if is_header_row(line):
            current_headers = extract_numbers(line) or re.split(r"\s{2,}", line)
            continue

        numbers = extract_numbers(line)

        if len(numbers) >= 3:
            course = re.split(r"\d", line, maxsplit=1)[0].strip()
            labeled = [f"{h}: {n}" for h, n in zip(
                ["GQ Fee", "MQ Fee", "NRI Fee"] * 10,
                numbers
            )]

            chunk = f"Course: {course}\n" + "\n".join(labeled)
            chunks.append(chunk)

    return chunks