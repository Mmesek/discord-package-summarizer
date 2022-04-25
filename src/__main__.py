from zipfile import Path, ZipFile

from models import Index
from utils import load_directory, load_file


def load_package(zip_file: ZipFile) -> Index:
    servers = {
        "servers": load_directory(zip_file, "servers", ["audit-log.json", "guild.json"]),
        "index": load_file(Path(zip_file, at="servers/index.json")),
    }
    messages = {
        "channels": load_directory(zip_file, "messages", ["channel.json", "messages.csv"]),
        "index": load_file(Path(zip_file, at="messages/index.json")),
    }
    index = Index()
    index.load_servers(servers["index"])
    index.load_channels(messages["index"])
    for channel, messages in messages["channels"].items():
        channel = int(channel.strip("c"))
        index.channels[channel].update_channel(messages["channel.json"])
        index.channels[channel].load_messages(messages["messages.csv"])
    return index


def print_table(table: list[tuple], title: str, by: int = 1, top: int = 10, start_at: int = 0) -> None:
    print(title, len(table))
    s = sorted(table, key=lambda x: int(x[by]), reverse=True)[start_at:top]
    print(
        "\n".join(
            [
                f"{x+1}. {i[0].replace('Direct Message with ', '')} - {i[2]} / {i[1]} = {i[2]/(i[1] or 1)}"
                for x, i in enumerate(s)
            ]
        )
    )
    print()


with ZipFile("package.zip", "r") as zip_file:
    index = load_package(zip_file)


def first_msg(index):
    f = index.message(1, None)[0]
    print("First Message:", f.channel.name, f.contents, f.timestamp)


def last_msg(index):
    l = index.message(None, start_=-1)[0]
    print("Last Message:", l.channel.name, l.contents, l.timestamp)


def list_top_dms(index):
    dms = list(filter(lambda x: "Direct Message with" in str(x[0]), index.channel_stats))
    print_table(dms, "DMs:", by=1)
    print_table(dms, "Character's per DM:", by=2)


def list_top_channels(index):
    channels = list(filter(lambda x: "Direct Message with" not in str(x[0]), index.channel_stats))
    print_table(channels, "Channels:", by=1)
    print_table(channels, "Character's per Channel:", by=2)


def plot_timeseries(index):
    import pandas as pd
    import matplotlib.pyplot as plt

    messages = index.message(None, 0)

    # points = [{"ts": pd.to_datetime(m.timestamp), "label": m.channel.name, "value": len(m.contents)} for m in messages]
    # indexes = [pd.to_datetime(m.timestamp) for m in messages]
    # msgs = [len(m.contents) for m in messages]
    # channels = [m.channel.name for m in messages]

    # df = pd.Series(msgs, indexes)
    by_channel = {}
    for m in messages:
        if m.channel.name not in by_channel:
            by_channel[m.channel.name] = {"y": [], "x": []}
        # by_channel[m.channel.name].append({"y":pd.to_datetime(m.timestamp), "x":len(m.contents)})
        by_channel[m.channel.name]["y"].append(pd.to_datetime(m.timestamp))
        by_channel[m.channel.name]["x"].append(len(m.contents))

    for label, channel in by_channel.items():
        df = pd.Series(channel["x"], index=channel["y"])
        df = df.resample("Y").count()
        plt.plot(df, label=label)
    plt.show()
