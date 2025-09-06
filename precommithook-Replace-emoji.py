#!/usr/bin/env python
import re
import sys

def remove_emoji(string):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

if __name__ == '__main__':
    for filename in sys.argv[1:]:
        with open(filename, 'r+', encoding='utf-8') as file:
            content = file.read()
            new_content = remove_emoji(content)
            if content != new_content:
                file.seek(0)
                file.write(new_content)
                file.truncate()