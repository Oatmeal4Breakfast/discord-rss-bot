import html2text


def main():
    print("Hello from discord-rss-bot!")

    parser = html2text.HTML2Text()
    print(type(parser))


if __name__ == "__main__":
    main()
