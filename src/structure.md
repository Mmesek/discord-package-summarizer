# Tree
package.zip structure's reference
```
account |
    user.json
    applications |
        list |
            application.json
activity |
    tns
    reporting
messages |
    index.json | 
        id
        name
    channel |
        channel.json |
            server |
                name: str
                id: int
                type: int
                guild |
                    id
                    name
            direct |
                id: int
                type: int
                recipents: list[int]
        messages.csv |
            ID
            Timestamp
            Contents
            Attachments
programs |
servers |
    index.json |
        id
        name
    server |
        guild.json |
        audit-log.json |
```